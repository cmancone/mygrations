class rows( object ):

    @property
    def raw_rows( self ):
        """ Public getter.  Returns a list of insert values from the VALUES part of the query

        :returns: A list of values for each row
        :rtype: list
        """

        return self._raw_rows

    @property
    def columns( self ):
        """ Public getter.  Returns the list of columns for the rows

        :returns: A list of columns
        :rtype: list
        """
        return self._columns
