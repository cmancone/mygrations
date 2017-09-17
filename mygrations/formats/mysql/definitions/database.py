class database( object ):

    _errors = None
    _warnings = None
    _tables = None
    _rows = None

    @property
    def tables( self ):
        """ Public getter.  Returns a dict of table definitions, by table name

        :returns: A dict of table definitions, by table name
        :rtype: list
        """
        return {} if self._tables is None else self._tables

    @property
    def errors( self ):
        """ Public getter.  Returns a list of parsing errors

        :returns: A list of parsing errors
        :rtype: list
        """
        return [] if self._errors is None else self._errors

    @property
    def warnings( self ):
        """ Public getter.  Returns a list of parsing/table warnings

        :returns: A list of parsing/table warnings
        :rtype: list
        """
        return [] if self._warnings is None else self._warnings

    def store_rows_with_tables( self ):
        """ Processes table rows and adds them to the appropriate tables

        Table rows are stored with tables for comparison purposes, but might
        come in through their own separate files.  This method puts the two
        together.
        """
        for rows in self._rows:
            if not rows.table in self._tables:
                self._errors.append( 'Found rows for table %s but that table does not have a definition' % rows.table )
                continue

            returned = self._tables[rows.table].add_rows( rows )
            if isinstance( returned, str ):
                self._errors.append( returned )

    def __sub__( self, new_db ):
        """ Compares two databases with eachother and returns a list of differences

        Specifically, it returns a list of mygrations.formats.definitions.operation objects.
        These objects will easily return an SQL command that will correct any differences.
        In other words, this pseudo code will make DB1 have the same structure as DB2

        for difference in DB2 - DB1:
            DB1.apply( difference )

        :param new_db: A database to find differences with
        :type new_db: mygrations.formats.mysql.definitions.database
        :returns: A list of differences
        :rtype: list
        """
        # start with the tables, obviously
        current_tables = set()
        new_tables = set()
        for table in self._tables.keys():
            current_tables.add( table )
        for table in new_db.tables.keys():
            new_tables.add( table )

        tables_to_add = current_tables - new_tables
        tables_to_remove = new_tables - current_tables

        # with the straightened out, we just need to check and see what
        # tables might differ
        operations = []
        for table in current_tables.intersection( new_tables ):
            diff = self._tables[table] - new_db.tables[table]
            if not diff:
                continue

            operations.extend( diff )

        # tables to remove must be checked for violations of foreign keys
        # tables to add must be added in proper order for foreign keys
        # foreign keys should probably be added completely separately,
        # although it would be nice to be smart
