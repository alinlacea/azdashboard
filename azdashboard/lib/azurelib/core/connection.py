from azure.storage.blob import BlobService
from azure.storage.queue import QueueService
from azure.storage.table import TableService

from azdashboard.lib.azurelib.core.errhandlers import azure_error
from azdashboard.lib.azurelib.queue import AzQueue
# from azurelib.storage import AzContainer, AzBlob
from azdashboard.lib.azurelib.table import AzTable


class AzConnection(object):

    """Connection instance for azurelib objects"""

    def __init__(self, user, key):
        """Args:
            user: Azure Storage username
            key: Azure Storage account key
        """

        super(AzConnection, self).__init__()
        self._user = user
        self._key = key

    @azure_error()
    def queue(self, name=None):
        """Creates an azurelib.AzQueue object and
        sets it's connection.
        Args:
            name: (optional) name of the azure queue."""

        service = QueueService(self._user, self._key)
        return AzQueue(service, name)

    @azure_error()
    def table(self, name=None):
        """Creates an azurelib.AzTable object and
        sets it's connection
        Args:
            name: (optional) name of the azure table."""

        service = TableService(self._user, self._key)
        return AzTable(service, name)

    @azure_error()
    def container(self, name):
        service = BlobService(account_name=self._user, account_key=self._key)
        return AzContainer(service, container_name=name)

    @azure_error()
    def blob(self, name):
        service = BlobService(account_name=self._user, account_key=self._key)
        return AzBlob(service, blob_name=name)

    def get_user(self):
        return self._user
