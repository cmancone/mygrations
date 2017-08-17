from collections import OrderedDict

class table( object ):

    @property
    def name( self ):
        """ Public getter.  Returns the name of the column.

        :returns: The column name
        :rtype: string
        """

        return self._name

    @property
    def options( self ):
        """ Public getter.  Returns a list of table options

        :returns: Table options
        :rtype: list
        """

        return self._options

    @property
    def columns( self ):
        """ Public getter.  Returns an ordered dictionary of table columns

        :returns: Table columns
        :rtype: OrderedDict
        """

        return self._columns

    @property
    def indexes( self ):
        """ Public getter.  Returns an ordered dictionary of table indexes

        :returns: Table indexes
        :rtype: OrderedDict
        """

        return self._indexes

    @property
    def constraints( self ):
        """ Public getter.  Returns an ordered dictionary of table constraints

        :returns: Table constraints
        :rtype: OrderedDict
        """

        return self._constraints

    @property
    def primary( self ):
        """ Public getter.  Returns the index object for the primary key

        :returns: The index object of the primary key column
        :rtype: isinstance(formats.mysql.definitions.index)
        """

        return self._primary
