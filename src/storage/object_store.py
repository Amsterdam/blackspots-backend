import logging
import os
from typing import List, Tuple

from django.conf import settings
from objectstore import get_full_container_list, get_connection
from swiftclient import ClientException

from datasets.blackspots.models import Document

DIR_CONTENT_TYPE = 'application/directory'

XLS_OBJECT_NAME = 'VVP_Blackspot_Voortgangslijst_Kaart_actueel.xls'
DOWNLOAD_DIR = '/tmp/blackspots/'
WBA_CONTAINER_NAME = f'wbalijst'
DOC_CONTAINER_NAME = f'doc'

DocumentList = List[Tuple[str, str]]

logger = logging.getLogger(__name__)


class ObjectStore:

    def __init__(self, config):
        self.config = config
        super().__init__()

    def get_connection(self):
        connection = get_connection(self.config)
        return connection

    def upload(self, file, document: Document):
        logger.info(f"Uploading {file} to objectstore: {document.filename}")
        connection = self.get_connection()

        container_path = ObjectStore.get_container_path(document.type)
        connection.put_object(container_path, document.filename, file)
        logger.info("Done uploading to objectstore")

    def delete(self, document: Document):
        logger.info(f"Deleting file {document.filename}")
        connection = self.get_connection()

        container_path = ObjectStore.get_container_path(document.type)
        try:
            connection.delete_object(container_path, document.filename)
        except ClientException:
            logger.info(f"Failed to delete object for document id {document.id}")

        logger.info("Done deleting file from objectstore")

    def get_document(self, connection, container_name: str, object_name: str):
        logger.debug(f'Fetching file from objectstore: {container_name}, {object_name}')
        return connection.get_object(container_name, object_name)

    def get_wba_documents_list(self, connection) -> DocumentList:
        """
        Get list of wba list documents from object store.
        :param connection: swiftclient connection
        :return: Array of documents in the form:
        [('rapportage', 'QE1_rapportage_Some_where - some extra info.pdf'), ... ]
        """
        documents_meta = get_full_container_list(connection, container=settings.OBJECTSTORE_ENV,
                                                 prefix=DOC_CONTAINER_NAME)
        documents_paths = [
            meta.get('name') for meta in documents_meta if
            meta.get('content_type') != DIR_CONTENT_TYPE
        ]
        return list(map(os.path.split, documents_paths))

    def get_file(self, connection, container_name: str, path: str, object_name: str):
        """
        Download the file from stack and store write it to the temp download folder
        :param connection: swiftclient connection object
        :param container_name The name of the container(acc or prod)
        :param path: the path where the object is stored you want to download
        :param object_name: The name of the object you want to download
        """
        os.makedirs(f'{DOWNLOAD_DIR}{container_name}/{path}', exist_ok=True)
        output_path = os.path.join(f'{DOWNLOAD_DIR}{container_name}/{path}', object_name)

        logger.info(f"Fetching file: {path}/{object_name}")
        new_data = connection.get_object(container_name, f'{path}/{object_name}')[1]
        with open(output_path, 'wb') as file:
            file.write(new_data)
        return output_path

    def fetch_spots(self, connection):
        return self.get_file(connection, settings.OBJECTSTORE_ENV, WBA_CONTAINER_NAME, XLS_OBJECT_NAME)

    @staticmethod
    def get_container_path(document_type):
        if document_type == Document.DocumentType.Ontwerp:
            return f'{settings.OBJECTSTORE_UPLOAD_CONTAINER_NAME}/doc/ontwerp'
        else:
            return f'{settings.OBJECTSTORE_UPLOAD_CONTAINER_NAME}/doc/rapportage'
