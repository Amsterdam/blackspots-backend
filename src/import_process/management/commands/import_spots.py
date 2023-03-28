import logging
import os
from typing import Optional

from datasets.blackspots.models import Document, Spot
from django.conf import settings
from django.core.management.base import BaseCommand

from import_process.clean import clear_models
from import_process.process_xls import process_xls
from storage.object_store import ObjectStore

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import blackspots from objectstore"

    def add_arguments(self, parser):
        # useful for local testing / debugging
        parser.add_argument("--xls_path", type=str, default=None)
        parser.add_argument(
            "--remove_existing_data",
            action="store_true",
            help="add --remove_existing_data to clean all records from the db before importing",
        )

    def handle(self, *args, **options):
        if not (xls_path := options.get("xls_path")):
            assert os.getenv("OBJECTSTORE_PASSWORD")
        perform_import(xls_path, options["remove_existing_data"])


def perform_import(xls_path: Optional[str], remove_existing_data: bool):
    """
    Perform an import from new spots and documents
    :param xls_path: path to the file to process, if None will be downloaded from the object store
    :param remove_existing_data: adding the parameter --remove_existing_data will clear all the records before importing
    """

    if remove_existing_data:
        log.info("Clearing models")
        clear_models()

    document_list = None
    if xls_path is None:
        objstore = ObjectStore(config=settings.OBJECTSTORE_CONNECTION_CONFIG)

        log.info("Opening object store connection")
        connection = objstore.get_connection()

        log.info("Getting documents list")
        document_list = objstore.get_wba_documents_list(connection)
        log.info(f"document list size: {len(document_list)}")

        log.info("Fetching xls file")
        xls_path = objstore.fetch_spots(connection)

    log.info("Importing xls file")
    process_xls(xls_path, document_list)

    log.info(f"Spot count: {Spot.objects.all().count()}")
    log.info(f"Document count: {Document.objects.all().count()}")
