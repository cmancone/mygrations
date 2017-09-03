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

    def ingest( self ):

        pass
