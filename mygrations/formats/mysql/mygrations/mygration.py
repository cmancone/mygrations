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
        self._operations = self._process()

    @property
    def operations( self ):
        """ Public getter.  Returns list of operations to bring db_from to db_to

        If db_from doesn't exist then it will be a list of operations to
        create db_to.

        :returns: A list of table operations
        :rtype: [mygrations.formats.mysql.mygrations.operations.operation]
        """
        return self._operations

    def __len__( self ):
        return len( self._operations )

    def __bool__( self ):
        return True if len( self._operations ) else False

    def __str__( self ):
        return "\n".join( [ str( x ) for x in self._operations ] )

    def __iter__( self ):
        return self._operations.__iter__()

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
            for new_table_name in tables_to_add:
                new_table = self.db_to.tables[new_table_name]
                problem_constraints = tracking_db.unfulfilled_fks( new_table )

                if not problem_constraints:
                    tables_to_add.remove( new_table_name )
                    operations.append( new_table.create() )
                    tracking_db.add_table( new_table )
                    continue

        # now we have the general todo list, but the reality
        # is much more complicated than that: in particular FK checks.
        # begin straightening it all out!

        # with the straightened out, we just need to check and see what
        # tables might differ
        #operations = []
        #for table in current_tables.intersection( new_tables ):
            #for operation in self.db1.tables[table].to( self.db2.tables[table] ):
                #print( operation )

        # tables to remove must be checked for violations of foreign keys
        # tables to add must be added in proper order for foreign keys
        # foreign keys should probably be added completely separately,
        # although it would be nice to be smart

        return operations
