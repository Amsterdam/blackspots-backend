import json
import logging
from ast import literal_eval
from typing import Optional

import xlrd
from django.contrib.gis.geos import Polygon, Point
from xlrd import open_workbook

from datasets.blackspots.models import Document, Spot
from import_process import util
from storage.objectstore import DocumentList

log = logging.getLogger(__name__)

EXCEL_STRUCTURE = {
    'number':                       {'column_idx': 0, 'header': 'Nummer'},
    'description':                  {'column_idx': 1, 'header': 'Locatie omschrijving'},
    'type':                         {'column_idx': 2, 'header': ''},  # Type
    'lat':                          {'column_idx': 3, 'header': 'Lat'},
    'lng':                          {'column_idx': 4, 'header': 'Long'},
    'wegvak':                       {'column_idx': 5, 'header': 'Wegvak'},  # was wegvak
    'stadsdeel':                    {'column_idx': 6, 'header': 'Stadsdeel'},
    'status':                       {'column_idx': 7, 'header': 'Status'},
    'actiehouders':                 {'column_idx': 8, 'header': 'Actiehouders'},
    'tasks':                        {'column_idx': 9, 'header': 'Taken'},
    'start_uitvoering':             {'column_idx': 10, 'header': 'Start uitvoering'},
    'eind_uitvoering':              {'column_idx': 11, 'header': 'Eind uitvoering'},
    'jaar_blackspot':               {'column_idx': 12, 'header': 'Jaar Blackspotlijst'},
    'jaar_quickscan':               {'column_idx': 13, 'header': 'Jaar ongeval quickscan rapportage'},
    'jaar_opgenomen_in_ivm_lijst':  {'column_idx': 14, 'header': 'Jaar opgenomen in IVM lijst'},
    'jaar_oplevering':              {'column_idx': 15, 'header': 'Jaar oplevering'},
    'notes':                        {'column_idx': 16, 'header': 'Opmerkingen'},
    'rapportage':                   {'column_idx': 17, 'header': 'Rapportage'},
    'ontwerp':                      {'column_idx': 18, 'header': 'Verkeersontwerp'},
}


def get_sheet_cell(sheet, column_name, row_idx):
    value = EXCEL_STRUCTURE.get(column_name)
    assert value is not None, f'column name not recognised: {column_name}'
    return sheet.cell_value(row_idx, value.get('column_idx'))


def get_sheet_date_cell(sheet, column_name, row_idx, date_mode):
    value = EXCEL_STRUCTURE.get(column_name)
    assert value is not None, f'column name not recognised: {column_name}'
    cell_value = sheet.cell_value(row_idx, value.get('column_idx'))
    if isinstance(cell_value, str):
        return cell_value
    datetime = xlrd.xldate.xldate_as_datetime(cell_value, date_mode)
    date_str = datetime.strftime("%d/%m/%y")
    return date_str


def assert_column_name(sheet, column_idx, expected):
    value = sheet.cell_value(0, column_idx).strip()
    assert value == expected, f'header {column_idx} is not expected value {expected} but {value}'


def check_column_names(sheet):
    for value in EXCEL_STRUCTURE.values():
        if value.get('skip', False):
            continue
        assert_column_name(sheet, value.get('column_idx'), value.get('header'))


class InputError(Exception):
    pass


class SkipError(InputError):
    pass


def log_error(message):
    log.error(message)


def get_integer(value, field_name):
    if value is None or value == ''\
            or str(value).lower() == 'onbekend'\
            or str(value).lower() == 'geen'\
            or str(value).lower() == 'n.v.t.':
        return None
    try:
        return int(value)
    except ValueError as e:
        log_error(f"Error parsing {value}, {field_name}: '{e}'")
        return None


def get_spot_type(abbreviation):
    excel_to_enum = {
        'B': Spot.SpotType.blackspot,
        'BW': Spot.SpotType.wegvak,
        'QD': Spot.SpotType.protocol_dodelijk,
        'QE': Spot.SpotType.protocol_ernstig,
        'R': Spot.SpotType.risicolocatie_ivm,
    }
    key = abbreviation.strip()
    if key == 'Q' or key == 'QSNP':
        raise SkipError(f'Q and QSNP not supported, type: {key}')

    value = excel_to_enum.get(key)
    if not value:
        raise InputError(f'Unkown type value: {abbreviation}')
    else:
        return value


def get_status(name: str):
    excel_to_enum = {
        'Onbekend': Spot.StatusChoice.onbekend,
        'Gereed': Spot.StatusChoice.gereed,
        'Voorbereiding': Spot.StatusChoice.voorbereiding,
        'Onderzoek/ ontwerp': Spot.StatusChoice.onderzoek_ontwerp,
        'Uitvoering': Spot.StatusChoice.uitvoering,
        'Geen maatregel': Spot.StatusChoice.geen_maatregel,
    }
    value = excel_to_enum.get(name.strip())
    if not value:
        raise SkipError(f'Unknown status value: {name}')
    else:
        return value


def get_stadsdeel(name: str):
    value = util.get_stadsdeel(name)
    if not value:
        raise InputError(f"Unknown stadsdeel: {name}")
    return value


def get_polygoon(input: str):
    if input:
        data = list(literal_eval(input))
        # ensure polygon is closed
        if data[-1] != data[0]:
            data.append(data[0])
        return Polygon(data)
    return None


def create_document(
        document_list: DocumentList,
        doc_type: Document.DocumentType,
        filename: str,
        spot: Spot
):
    if not filename or len(filename) == 0 or not document_list:
        return

    available_filenames = [filename for [_, filename] in document_list]
    if filename not in available_filenames:
        log_error(f'Missing file on object store: {filename} of type {doc_type}')
        return

    Document.objects.create(type=doc_type, filename=filename, spot=spot)


def process_xls(xls_path, document_list: Optional[DocumentList]):
    book = open_workbook(xls_path)

    sheet = book.sheet_by_index(0)

    check_column_names(sheet)

    for row_idx in range(1, sheet.nrows):

        # one of point or wegvaks should be present
        latitude = get_sheet_cell(sheet, 'lat', row_idx)
        longitude = get_sheet_cell(sheet, 'lng', row_idx)
        wegvak = get_sheet_cell(sheet, 'wegvak', row_idx)

        point, polygoon = None, None
        try:
            point = Point(longitude, latitude)
        except Exception as point_e:
            try:
                polygoon = get_polygoon(wegvak)
            except Exception as polygoon_e:
                log_error(f"Unknown point/wegvak: {latitude}, {longitude} : "
                          f" \"{point_e}\", {wegvak}: \"{polygoon_e}\", skipping")
                continue

        stadsdeel = get_stadsdeel(get_sheet_cell(sheet, 'stadsdeel', row_idx))

        jaar_blackspotlijst = get_integer(get_sheet_cell(sheet, 'jaar_blackspot', row_idx), 'blackspotlijst')
        jaar_quickscan = get_integer(get_sheet_cell(sheet, 'jaar_quickscan', row_idx), 'quickscan')
        try:
            spot_type = get_spot_type(get_sheet_cell(sheet, 'type', row_idx))
            status = get_status(get_sheet_cell(sheet, 'status', row_idx))
        except SkipError as e:
            log_error(f"\"{e}\", skipping")
            continue
        spot_data = {
            "locatie_id": get_sheet_cell(sheet, 'number', row_idx),
            "actiehouders": get_sheet_cell(sheet, 'actiehouders', row_idx),
            "spot_type": spot_type,
            "description": get_sheet_cell(sheet, 'description', row_idx),
            "point": point,
            "polygoon": polygoon,
            "stadsdeel": stadsdeel,
            "status": status,

            "start_uitvoering": get_sheet_date_cell(sheet, 'start_uitvoering', row_idx, book.datemode),
            "eind_uitvoering": get_sheet_date_cell(sheet, 'eind_uitvoering', row_idx, book.datemode),
            "tasks": get_sheet_cell(sheet, 'tasks', row_idx),
            "notes": get_sheet_cell(sheet, 'notes', row_idx),

            "jaar_blackspotlijst": jaar_blackspotlijst,
            "jaar_ongeval_quickscan": jaar_quickscan,
            "jaar_oplevering": get_integer(get_sheet_cell(sheet, 'jaar_oplevering', row_idx), 'oplevering'),
            "jaar_opgenomen_in_ivm_lijst": get_integer(
                get_sheet_cell(sheet, 'jaar_opgenomen_in_ivm_lijst', row_idx),
                'jaar_opgenomen_in_ivm_lijst'
            ),
        }

        [spot, _] = Spot.objects.get_or_create(**spot_data)

        create_document(document_list,
                        Document.DocumentType.Rapportage,
                        get_sheet_cell(sheet, 'rapportage', row_idx),
                        spot)

        create_document(document_list,
                        Document.DocumentType.Ontwerp,
                        get_sheet_cell(sheet, 'ontwerp', row_idx),
                        spot)
