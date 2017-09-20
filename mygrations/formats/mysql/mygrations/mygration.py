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
    def __init__( self, db1, db2 = None ):
        """ Create a migration plan

        :param db1: The target database structure to migrate to
        :param db2: The current database structure to migrate from
        :type db1: mygrations.formats.mysql.definitions.database
        :type db2: mygrations.formats.mysql.definitions.database
        """

        self.db1 = db1
        self.db2 = db2
        self._process()

    def _process( self ):

        # start with the tables, obviously
        new_tables = set()
        current_tables = set()
        for table in self.db1.tables.keys():
            new_tables.add( table )
        if self.db2:
            for table in self.db2.tables.keys():
                current_tables.add( table )

        tables_to_add = current_tables - new_tables
        tables_to_remove = new_tables - current_tables
        tables_to_update = new_tables.intersection( current_tables )

        # now we have the general todo list, but the reality
        # is much more complicated than that: in particular FK checks.
        # begin straightening it all out!

        # with the straightened out, we just need to check and see what
        # tables might differ
        operations = []
        for table in current_tables.intersection( new_tables ):
            for operation in self.db1.tables[table] - self.db2.tables[table]:
                print( operation )

        # tables to remove must be checked for violations of foreign keys
        # tables to add must be added in proper order for foreign keys
        # foreign keys should probably be added completely separately,
        # although it would be nice to be smart
