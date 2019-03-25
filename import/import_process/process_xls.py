import logging
import random

from django.contrib.gis.geos import Point
from xlrd import open_workbook

from datasets.blackspots.models import Spot


log = logging.getLogger(__name__)


class InputError(Exception):
    pass


def log_error(message):
    log.error(message)


def get_integer(field, field_name):
    try:
        return int(field)
    except ValueError as e:
        log_error(f"Error parsing {field}, {field_name}: '{e}'")
        return None


def get_spot_type(jaar_blackspotslijst, jaar_quickscan):
    if jaar_blackspotslijst:
        return Spot.SpotType.blackspot
    if jaar_quickscan:
        if random.choice([True, False]):
            return Spot.SpotType.protocol_ernstig
        else:
            return Spot.SpotType.protocol_dodelijk
    return random.choice([Spot.SpotType.risico, Spot.SpotType.wegvak])


def get_status(name: str):
    excel_to_enum = {
        'Onbekend': Spot.StatusChoice.onbekend,
        'Gereed': Spot.StatusChoice.gereed,
        'Voorbereiding': Spot.StatusChoice.voorbereiding,
        'Onderzoek/ ontwerp': Spot.StatusChoice.onderzoek_ontwerp,
        'Uitvoering': Spot.StatusChoice.uitvoering,
        'Geen maatregel': Spot.StatusChoice.geen_maatregel,
    }
    value = excel_to_enum.get(name)
    if not value:
        raise InputError(f'Unkown status value: {name}')
        return Spot.StatusChoice.onbekend
    else:
        return value
    return Spot.StatusChoice.geen_maatregel


def process_xls(xls_path):
    book = open_workbook(xls_path)

    sheet = book.sheet_by_index(0)

    for row_idx in range(1, sheet.nrows):
        latitude = sheet.cell(row_idx, 2).value
        longitude = sheet.cell(row_idx, 3).value
        try:
            point = Point(longitude, latitude)
        except TypeError as e:
            log_error(f"Unkown point: {latitude}, {longitude}: \"{e}\", skipping")
            continue

        stadsdeel = sheet.cell(row_idx, 4).value
        if len(stadsdeel) != 1:
            log_error(f"Unkown stadsdeel: {stadsdeel}, skipping")
            continue

        jaar_blackspotlijst = get_integer(sheet.cell(row_idx, 14).value, 'blackspotlijst')
        jaar_quickscan = get_integer(sheet.cell(row_idx, 15).value, 'quickscan')
        spot_type = get_spot_type(jaar_blackspotlijst, jaar_quickscan)
        spot_data = {
            "locatie_id": sheet.cell(row_idx, 0).value,
            "spot_type": spot_type,
            "description": sheet.cell(row_idx, 1).value,
            "point": point,
            "stadsdeel": stadsdeel,
            "status": get_status(sheet.cell(row_idx, 5).value),
            "jaar_blackspotlijst": jaar_blackspotlijst,
            "jaar_ongeval_quickscan": jaar_quickscan,
            "jaar_oplevering": get_integer(sheet.cell(row_idx, 16).value, 'oplevering'),
        }

        Spot.objects.get_or_create(**spot_data)

    log.info(f'Spot count: {Spot.objects.all().count()}')
