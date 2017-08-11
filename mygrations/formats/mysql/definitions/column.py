class column( object ):

    definition_type = 'column'
    _unsigned = None
    _character_set = None
    _collate = None
    _auto_increment = None

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
        return None if self._character_set is None else self._collate.upper()

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
