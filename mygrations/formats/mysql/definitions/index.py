class index( object ):

    _name = ''
    _index_type = ''
    _columns = None
    _errors = None
    _warnings = None

    @property
    def name( self ):
        """ Public getter.  Returns the name of the column.

        :returns: The index name
        :rtype: string
        """

        return self._name

    @property
    def index_type( self ):
        """ Public getter.  Returns a string denoting the type of the index.  Always returns in uppercase

        Index type can be 'INDEX', 'UNIQUE', or 'PRIMARY'

        :returns: The index type
        :rtype: string
        """
        return self._index_type.upper()

    @property
    def columns( self ):
        """ Public getter.  Returns a list of the column names on the index.

        :returns: The column length
        :rtype: list
        """

        return self._columns

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
