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
        for (table,rows) in self._rows.items():
            if not rows.table in self._tables:
                self._errors.append( 'Found rows for table %s but that table does not have a definition' % rows.table )
                continue

            self._tables[rows.table].add_rows( rows )
