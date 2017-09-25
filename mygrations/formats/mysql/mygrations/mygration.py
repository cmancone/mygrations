import copy
from mygrations.formats.mysql.definitions.database import database

class mygration:
    """ Creates a migration plan to update a database to a given spec.

    If only one database is passed in, it treats it as a structure to migrate
    to starting from a blank slate, which primariliy means just figuring out
    what order to add tables in to account for foreign key constraints.

    If two tables are present, then it will treat the second as the current
    database constraint, and will figure out steps to execute in action
    to update that second database to match the structure of the first.

    The general steps are:

    1. Add/update columns that exist in both, temporarily skipping FK constraints that aren't yet fulfilled
    2. Remove any foreign keys that don't exist in the target database structure
    3. Add new tables in order necessitated by FK constraints.  Temporarily skip any FK constraints that can't be fulfilled yet
    4. Add in all FKs that were previously skipped
    5. Remove any columns that do not exist in the target database structure, noting an error if a FK is violated
    6. Remove any tables that do not exist in the target database structure, noting an error if a FK is violated
    """
    def __init__( self, db_to, db_from = None ):
        """ Create a migration plan

        :param db_to: The target database structure to migrate to
        :param db_from: The current database structure to migrate from
        :type db_to: mygrations.formats.mysql.definitions.database
        :type db_from: mygrations.formats.mysql.definitions.database
        """

        self.db_to = db_to
        self.db_from = db_from
        self._process()

    def _differences(self, a, b):
        """
        Calculates the difference between two OrderedDicts.

        https://codereview.stackexchange.com/a/176303/140581

        Duplication!!!! (formats.mysql.create_parser).  Sue me.

        :param a: OrderedDict
        :param b: OrderedDict
        :return: (added, removed, overlap)
        """

        return (
            [key for key in b if key not in a],
            [key for key in a if key not in b],
            [key for key in a if key in b]
        )

    def _process( self ):

        operations = []
        # throughout this process we have to keep track of what tables and columns we have
        # the simplest way to do this is with a database object.
        tracking_db = copy.deepcopy( self.db_from ) if self.db_from else database()

        # start with the tables, obviously
        db_from_tables = self.db_from.tables if self.db_from else {}
        ( tables_to_add, tables_to_remove, tables_to_update ) = self._differences( db_from_tables, self.db_to.tables )

        # keep looping through tables as long as we find some to process
        last_number_to_add = 0
        while tables_to_add and len( tables_to_add ) != last_number_to_add:
            last_number_to_add = len( tables_to_add )
            for table in tables_to_add:
                if tracking_db.fulfills_fks( self.db_to.tables[table] ):
                    tables_to_add.remove( table )
                    operations.append( self.db_to.tables[table].create() )

        # now we have the general todo list, but the reality
        # is much more complicated than that: in particular FK checks.
        # begin straightening it all out!

        # with the straightened out, we just need to check and see what
        # tables might differ
        operations = []
        for table in current_tables.intersection( new_tables ):
            for operation in self.db1.tables[table].to( self.db2.tables[table] ):
                print( operation )

        # tables to remove must be checked for violations of foreign keys
        # tables to add must be added in proper order for foreign keys
        # foreign keys should probably be added completely separately,
        # although it would be nice to be smart
