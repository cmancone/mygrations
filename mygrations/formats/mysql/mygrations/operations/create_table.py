class create_table:
    """ Generates an SQL command to create a table """

    def __init__( self, table ):
        """ Create table constructor

        :param table: The table to build a create table command for
        :type table: formats.mysql.definitions.table
        """
        self.table = table

    @property
    def table_name( self ):
        """ Public getter.  Returns the name of the table.

        :returns: The table name
        :rtype: string
        """

        return self.table.name

    def __str__( self ):
        body = [ str( self.table.columns[col] ) for col in self.table.columns ]
        body.extend( [ str( self.table.indexes[index] ) for index in self.table.indexes ] )
        body.extend( [ str( self.table.constraints[constraint] ) for constraint in self.table.constraints ] )
        options = [ '%s=%s' % ( opt.name, opt.value  ) for opt in self.table.options ]
        if options:
            options = ' %s' % ' '.join( options )
        else:
            options = ''
        return 'CREATE TABLE `%s` (%s)%s;' % ( self.table.name, ",\n".join( body ), options )
