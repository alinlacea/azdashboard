class AzEntity(object):

    """Base class for Azurelib objects"""

    def __init__(self, service, name):
        """Creates an Azurelib AzEntity
        Args:
            service: either a azure.storage.TableService
                      or a azure.storage.QueueService
            name: entity's name. May be None
        """

        super(AzEntity, self).__init__()
        self._service = service
        self.select(name)

    def select(self, name):
        """Sets the entity's name. Required for
        operations on live Azure instances"""
        if name:
            name = name.replace("_", "")
            # from azurelib.storage import AzBlob
            #
            # if not isinstance(self, AzBlob):
            name = name.replace(".", "")
        self._name = name

    def get_name(self):
        """Returns the entity's name"""

        return self._name

    def get_service(self):
        """Returns the entity's service"""

        return self._service
