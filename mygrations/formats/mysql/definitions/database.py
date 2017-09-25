from mygrations.formats.mysql.mygrations.mygration import mygration

class database( object ):

    _errors = None
    _warnings = None
    _tables = None
    _rows = None

    def __init__( self ):
        self._warnings = []
        self._errors = []
        self._tables = {}
        self._rows = []

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

    def to( self, new_db ):
        """ Compares two databases with eachother and returns a mygration object that builds an action plan to bring the database up-to-spec with the new one

        The mygration object can generate SQL commands that will correct any differences.
        In other words, this pseudo code will make DB1 have the same structure as DB2

        for operation in DB1.to( DB2 ):
            DB1.apply( difference )

        :param new_db: A database to find differences with
        :type new_db: mygrations.formats.mysql.definitions.database
        :returns: A migration object that can adjust one database to match the other
        :rtype: mygrations.formats.mysql.mygrations.mygration
        """
        return mygration( new_db, self )

    def fulfills_fks( self, table ):
        """ Returns True or a list of constraints to denote whether or not the database structure can support the foreign keys for the table

        If all foreign keys are fulfilled by the database structure then True is returned
        If some foreign keys are unmet then a list of the unsupported FKs is returned
        If a foreign key exists but a structure mismatch would cause a 1215 error, a ValueError will be raised

        :param table: The table to check
        :type table: mygrations.formats.mysql.definitions.table
        :return: True if the foreign keys are supported or a list of which columns are not supported
        :rtype: True|list[mygrations.formats.mysql.definitions.constraint]
        """
        if not table.constraints:
            return True

        unsupported = []
        for constraint in table.constraints:
            if constraint.foreign_table not in self.tables:
                unsupported.append( constraint )
                continue
            foreign_table = self.tables[constraint.foreign_table]
            if constraint.foreign_column not in foreign_table:
                unsupported.append( constraint )
                continue

            # the column exists but we may still have a 1215 error.  That can happen in a few ways
            table_column = table.columns[constraint.column]
            foreign_column = foreign_table[constraint.foreign_column]
            if table_column.column_type != foreign_column.column_type:
                raise ValueError( "MySQL 1215 error for foreign key %s for '%s.%s': type of '%s' does not match type '%s' from '%s.%s'" % ( constraint.name, table.name, constraint.column, table_column.column_type, foreign_column.column_type, foreign_table.name, foreign_column.name ) )


        return unsupported if unsupported else True

