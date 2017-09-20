from mygrations.formats.mysql.mygrations.mygration import mygration

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
        """ Compares two databases with eachother and returns a mygration object that builds an action plan to bring the second up-to-spec with the first

        The mygration object can generate SQL commands that will correct any differences.
        In other words, this pseudo code will make DB1 have the same structure as DB2

        for difference in (DB2 - DB1):
            DB1.apply( difference )

        :param new_db: A database to find differences with
        :type new_db: mygrations.formats.mysql.definitions.database
        :returns: A migration object that can adjust one database to match the other
        :rtype: mygrations.formats.mysql.mygrations.mygration
        """
        return mygration( self, new_db )
