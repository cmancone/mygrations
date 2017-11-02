class index( object ):

    _name = ''
    _index_type = ''
    _columns = None
    _errors = None
    _warnings = None

    def __init__( self, name, columns, index_type='INDEX' ):
        """ Index constructor

        :param name: The name of the index
        :param columns: The columns in the index
        :param index_type: The type of the index (INDEX, UNIQUE, or PRIMARY)
        :type name: string
        :type columns: [string]
        :type index_type: string
        """
        self._name = name
        self._index_type = index_type
        self._columns = columns

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

    def __str__( self ):
        """ Returns the MySQL command that would create the column

        i.e. column_name type(len) default ''

        :returns: A partial MySQL command that could be used to generate the column
        :rtype: string
        """
        parts = []
        if self.index_type == 'PRIMARY':
            parts.append( 'PRIMARY' )
        elif self.index_type == 'UNIQUE':
            parts.append( 'UNIQUE' )
        parts.append( 'KEY' )

        if self.name:
            parts.append( '`%s`' % self.name )
        parts.append( '(`%s`)' % ( "`,`".join( self.columns ) ) )

        return ' '.join( parts )
