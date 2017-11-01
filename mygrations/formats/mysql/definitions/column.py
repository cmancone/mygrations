class column( object ):

    definition_type = 'column'
    _unsigned = None
    _character_set = None
    _collate = None
    _auto_increment = None
    _errors = None
    _warnings = None

    def __init__( self, name='', length='255', null=True, column_type='VARCHAR', default=None, unsigned=None, character_set='', collate='', auto_increment=False ):
        self._name = name
        self._length = length
        self._null = null
        self._column_type = column_type
        self._default = default
        self._unsigned = unsigned
        self._character_set = character_set
        self._collate = collate
        self._auto_increment = auto_increment

    @property
    def name( self ):
        """ Public getter.  Returns the name of the column.

        :returns: The column name
        :rtype: string
        """

        return self._name

    @property
    def length( self ):
        """ Public getter.  Returns the length of the column as a string.

        Some examples of the length for various column definitions:

        ==================  ====================
        Type                Length
        ==================  ====================
        INT(10) UNSIGNED    10
        VARCHAR(255)        255
        decimal(20,5)       20,5
        date
        ==================  ====================

        :returns: The column length
        :rtype: string
        """

        return self._length

    @property
    def null( self ):
        """ Public getter.  Returns True/False to denote if the column is allowed to be null

        :returns: Whether or not null is an allowed value for the column
        :rtype: bool
        """
        return self._null

    @property
    def column_type( self ):
        """ Public getter.  Returns a string denoting the type of the column.  Always returns in uppercase

        Some examples of the length for various column definitions:

        ==================  ====================
        Definition          Type
        ==================  ====================
        INT(10) UNSIGNED    INT
        VARCHAR(255)        VARCHAR
        decimal(20,5)       DECIMAL
        date                DATE
        ==================  ====================

        :returns: The column type
        :rtype: string
        """
        return self._column_type.upper()

    @property
    def default( self ):
        """ Public getter.  Returns the default value for the column as a string, or None for a default value of null

        Returns None to represent a default value of null.

        :returns: The default value
        :rtype: string|None
        """
        return self._default

    @property
    def unsigned( self ):
        """ Public getter.  Returns True, False, or None to denote the status of the UNSIGNED property

        ==================  ====================
        Return Value        Meaning
        ==================  ====================
        True                The column is unsigned
        False               The column is signed
        None                UNSIGNED is not an applicable property for this column type
        ==================  ====================

        :returns: True, False, or None
        :rtype: bool|None
        """
        return self._unsigned

    @property
    def character_set( self ):
        """ Public getter.  Returns None or a value to denote the CHARACTER_SET property

        :returns: string, or None
        :rtype: string|None
        """
        return None if self._character_set is None else self._character_set.upper()

    @property
    def collate( self ):
        """ Public getter.  Returns None or a value to denote the COLLATE property

        :returns: string, or None
        :rtype: string|None
        """
        return None if self._collate is None else self._collate.upper()

    @property
    def auto_increment( self ):
        """ Public getter.  Returns True, False, or None to denote the status of the AUTO_INCREMENT property

        ==================  ====================
        Return Value        Meaning
        ==================  ====================
        True                The column is an AUTO_INCREMENT column
        False               The column is not an AUTO_INCREMENT column
        None                AUTO_INCREMENT is not an applicable property for this column type
        ==================  ====================

        :returns: True, False, or None
        :rtype: bool|None
        """
        return self._auto_increment

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
        parts.append( '`%s`' % self.name )

        type_string = self.column_type
        if self.length:
            if type( self.length ) == type( [] ):
                length = "'%s'" % ( "','".join( self.length ) )
            else:
                length = self.length
            type_string += '(%s)' % length
        parts.append( type_string )

        if self.unsigned:
            parts.append( 'UNSIGNED' )

        if not self.null:
            parts.append( 'NOT NULL' )

        if self.default is not None:
            if self.default == '':
                parts.append( "DEFAULT ''" )
            elif self.default.isnumeric():
                parts.append( "DEFAULT %s" % self.default )
            else:
                parts.append( "DEFAULT '%s'" % self.default )

        if self.auto_increment:
            parts.append( 'AUTO_INCREMENT' )

        if self.character_set:
            parts.append( "CHARACTER SET '%s'" % self.character_set )

        if self.collate:
            parts.append( "COLLATE '%s'" % self.collate )

        return ' '.join( parts )

    def is_really_the_same_as( self, column ):
        """ Takes care of a pesky false-positive when checking columns

        :param column: The column to comprehensively check for a difference with
        :type column: mygrations.formats.mysql.definitions.column
        :returns: True if the column really is the same, even for apparent differences
        :rtype: bool
        """
        # if any of these attributes change then it really isn't the same
        for attr in [ 'name', 'length', 'null', 'column_type', 'unsigned' ]:
            if getattr( self, attr ) != getattr( column, attr ):
                return False

        # default needs a special check because it can run into issues for decimal columns
        if self.column_type == 'DECIMAL':
            split = self.length.split(',')
            if len( split ) == 2:
                ndecimals = int( split[1] )
                if ( self.default is None and column.default is not None ) or ( self.default is not None and column.default is None ):
                    return False
                if round( float( self.default ), ndecimals ) != round( float( column.default ), ndecimals ):
                    return False
        else:
            if self.default != column.default:
                return False

        # if collate or character_set are different and *both* have a value,
        # then these aren't really the same
        for attr in [ 'collate', 'character_set' ]:
            my_val = getattr( self, attr )
            that_val = getattr( column, attr )
            if my_val and that_val and my_val != that_val:
                return False

        # if we got here then these columns are the same. Either all attributes have the same
        # values, or collate and/or character_set differ, but they differ by one not having
        # a value.  This is the false-positive we are trying to check for
        # (see tests.formats.mysql.definitions.test_table_text_false_positives)
        return True
