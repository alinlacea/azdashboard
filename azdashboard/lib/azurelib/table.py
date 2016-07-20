from azdashboard.lib.azurelib.core.entity import AzEntity
from azdashboard.lib.azurelib.core.errhandlers import azure_error


class AzTable(AzEntity):

    """Object representing a live Azure Table"""

    def __init__(self, service, name):
        super(AzTable, self).__init__(service, name)
        self._partition = None

    @azure_error()
    def create(self, fail_on_exist=False):
        """Create the table on the connection's account"""

        self._service.create_table(self._name, fail_on_exist=fail_on_exist)
        return True

    @azure_error()
    def delete(self, fail_not_exist=False):
        """Delete the table from the account"""

        self._service.delete_table(self._name, fail_not_exist=fail_not_exist)
        return True

    @azure_error(suppress=[404])
    def exists(self):
        """Returns True if the table exists on
        the connection's account."""

        tables = self._service.query_tables(table_name=self._name)
        if tables and len(tables) > 0:
            return True
        return False

    @azure_error()
    def get(self, row, partition=None, selection=[]):
        """Gets the entity that has the specific row key.
        Args:
            row: the RowKey that is searched.
            partition: the PartitionKey is searched.
                if None, the set partition is used
            selection: list of strings specifing the columns
                to be retrieved
        Returns:
            dictionary with data & metadata
            See library's README for more details
        """

        if not partition:
            partition = self._partition
        selected = ", ".join(selection)
        entities = self._service.get_entity(self._name,
                                            partition,
                                            row,
                                            select=selected)
        dicts = entities.__dict__
        return dicts

    @azure_error()
    def insert(self, entity):
        """Inserts the provided entity into the table.
        Args:
            entity: dict that needs to contain at least
                the 'RowKey' key.
                If 'PartitionKey' is missing, it uses the set
                PartitionKey.
        """

        if "PartitionKey" not in entity:
            entity["PartitionKey"] = self._partition
        self._service.insert_entity(self._name, entity)
        return True

    @azure_error()
    def upsert(self, entity):
        """Inserts or merges the provided entity. Ignores etags.
        Args:
            entity: dict that needs to contain at least
                the 'RowKey' key.
                If 'PartitionKey' is missing, it uses the set
                PartitionKey.
        """

        if "PartitionKey" not in entity:
            entity["PartitionKey"] = self._partition
        self._service.insert_or_merge_entity(self._name,
                                             entity["PartitionKey"],
                                             entity["RowKey"],
                                             entity)
        return True

    @azure_error()
    def update(self, entity):
        """Merges the provided entity. Does
        consider etags.
        Args:
            entity: dict that needs to contain at least
                the 'RowKey' key.
                If 'PartitionKey' is missing, it uses the set
                PartitionKey.
                For the concurrency model to be used,
                also requires the 'Etag' key to be set.
                Otherwise, tries an insert.
        """

        if "PartitionKey" not in entity:
            entity["PartitionKey"] = self._partition
        if "ETag" in entity:
            etag = entity.pop("Etag")
            self._service.merge_entity(self._name,
                                       entity["PartitionKey"],
                                       entity["RowKey"],
                                       entity,
                                       if_match=etag)
        else:
            return self.insert(entity)
        return True

    @azure_error()
    def query(self, query, selection, top=1000):
        """Queries the table.
        Args:
            query: string.
                See http://msdn.microsoft.com/en-us/library/azure/dd894031.aspx
            selection: list of columns to be selected
        Returns:
            list of dict objects representing the queried entities
        """

        select = ", ".join(selection)
        done = False
        dicts = []
        next = {
            "nextpartitionkey": None,
            "nextrowkey": None
        }
        while not done:
            entities = self._service.query_entities(self._name,
                                                    filter=query,
                                                    select=select,
                                                    top=top,
                                                    next_partition_key=next["nextpartitionkey"],
                                                    next_row_key=next["nextrowkey"])
            for entity in entities:
                dicts.append(entity.__dict__)
            if hasattr(entities, "x_ms_continuation"):
                next["nextpartitionkey"] = entities.x_ms_continuation["nextpartitionkey"]
                next["nextrowkey"] = entities.x_ms_continuation["nextrowkey"]
            else:
                done = True
        return dicts

    @azure_error()
    def remove(self, row, partition=None, etag=None):
        """Deletes the provided entity. Considers etags.
        Args:
            entity: dict that needs to contain at least
                the 'RowKey' key.
                If 'PartitionKey' is missing, it uses the set
                PartitionKey.
        """

        if not partition:
            partition = self._partition
        if not etag:
            etag = "*"
        self._service.delete_entity(self._name,
                                    partition,
                                    row,
                                    if_match=etag)
        return True

    @azure_error()
    def list_tables(self):
        """List all tables from the account"""

        tables = self._service.query_tables()
        dicts = [table.__dict__ for table in tables]
        return dicts

    def set_partition(self, partition):
        """Sets the table's active partition."""

        self._partition = partition
