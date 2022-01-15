import copy

from mygrations.formats.mysql.definitions.database import Database
from mygrations.formats.mysql.mygrations.operations.row_insert import RowInsert
from mygrations.formats.mysql.mygrations.operations.row_delete import RowDelete
from mygrations.formats.mysql.mygrations.operations.row_update import RowUpdate
class RowMygration:
    """ Creates a migration plan to sync the rows of a database for tables being tracked.

    This doesn't sync rows for all tables but only those tables marked as
    tracking_rows
    """
    def __init__(self, db_to, db_from=None):
        """ Create a migration plan

        The row migrator assumes that both databases have already read rows into the
        table objects.  In standard usage, the files database will automatically
        read in the table rows (i.e. mygrations.formats.mysql.file_reader.database),
        but the actual database reader (mygrations.formats.mysql.db_reader.database)
        will not.  This is because, in normal usage, only the rows in *some* tables
        are tracked.  Which tables to track rows for is normally denoted by the fact
        that the *.sql files have inserts in them, which the file_reader picks up on.
        Then, the db_reader is told to read rows in only for those tables where the
        file_reader is tracking rows.  I.e.:

        >>> for table in files_database.tables.values():
        >>>     if not table.tracking_rows or table.name not in live_database.tables:
        >>>         continue
        >>>     live_database.read_rows( table )

        :param db_to: The target database rows to migrate to
        :param db_from: The current database rows to migrate from
        :type db_to: mygrations.formats.mysql.definitions.database
        :type db_from: mygrations.formats.mysql.definitions.database
        """
        self.db_to = db_to
        self.db_from = db_from

        # unlike with the structure migration, we figure out what are operations
        # are and then make sure those operations won't cause any 1215 errors
        self._operations = self._process()

        self._errors_1215 = []

    @property
    def operations(self):
        """ Public getter.  Returns list of operations to bring rows in db_from to match db_to

        If db_from doesn't exist then it will be a list of operations to
        create the rows in db_to.

        If the two databases have the exact same  rows for tables that are tracking_rows
        then operations will be an empty list

        :returns: A list of table row operations
        :rtype: None|[mygrations.formats.mysql.mygrations.operations.operation]
        """
        return self._operations

    @property
    def errors_1215(self):
        """ Public getter.  Returns list of 1215 errors (as strings)

        :returns: A list of 1215 error messages
        :rtype: [string]
        """
        return self._errors_1215

    def __len__(self):
        return len(self._operations)

    def __bool__(self):
        return True if len(self._operations) else False

    def __str__(self):
        return "\n".join([str(x) for x in self._operations])

    def __iter__(self):
        return self._operations.__iter__()

    def _process(self):
        """ Figures out the row operations needed to get to self.db_to

        Returns a list of operations that will migrate rows in db_from to db_to

        :return: Operations needed to complete the migration
        :rtype: [mygrations.formats.mysql.mygrations.operations]
        """
        operations = []
        tracking_tables = [table.name for table in self.db_to.tables.values() if table.tracking_rows]
        for table_name in tracking_tables:
            from_table = self.db_from.tables[table_name] if (
                self.db_from and table_name in self.db_from.tables
            ) else None
            more_operations = self.db_to.tables[table_name].to_rows(from_table)
            if not more_operations:
                continue

            operations.extend(more_operations)

        return operations
