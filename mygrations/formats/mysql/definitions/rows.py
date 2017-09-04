class rows( object ):

    _table = ''
    _raw_rows = ''
    _columns = None
    _errors = None
    _warnings = None

    @property
    def table( self ):
        """ Public getter.  Returns the name of the table that records are being inserted for

        :returns: The name of the table
        :rtype: list
        """

        return self._table

    @property
    def raw_rows( self ):
        """ Public getter.  Returns a list of insert values from the VALUES part of the query

        :returns: A list of values for each row
        :rtype: list[list]
        """

        return self._raw_rows

    @property
    def columns( self ):
        """ Public getter.  Returns the list of columns for the rows

        :returns: A list of columns
        :rtype: list
        """
        return self._columns

    @property
    def num_explicit_columns( self ):
        """ Public getter.  Returns the number of columns specified in the insert query

        Can be zero if none are specified, which happens for queries like:
        INSERT INTO table (val1, val2, val3...);

        :returns: The number of columns which have been explicitly defined
        :rtype: integer
        """
        return self._num_explicit_columns

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
