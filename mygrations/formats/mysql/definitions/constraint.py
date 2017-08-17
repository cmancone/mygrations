class constraint( object ):

    @property
    def name( self ):
        """ Public getter.  Returns the name of the column.

        :returns: The index name
        :rtype: string
        """

        return self._name

    @property
    def column( self ):
        """ Public getter.  Returns the name of the column this constraint is on

        :returns: The column name
        :rtype: string
        """

        return self._column

    @property
    def foreign_table( self ):
        """ Public getter.  Returns the name of the table this constraint is to

        :returns: The table name
        :rtype: string
        """

        return self._foreign_table

    @property
    def foreign_column( self ):
        """ Public getter.  Returns the name of the column in the foreign table this constraint is to

        :returns: The column name
        :rtype: string
        """

        return self._foreign_column

    @property
    def on_delete( self ):
        """ Public getter.  Returns the ON DELETE action for this constraint

        :returns: The ON DELETE action
        :rtype: string
        """

        return self._on_delete

    @property
    def on_update( self ):
        """ Public getter.  Returns the ON UPDATE action for this constraint

        :returns: The ON UPDATE action
        :rtype: string
        """

        return self._on_update
