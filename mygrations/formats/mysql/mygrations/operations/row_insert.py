class row_insert:
    """ Generates an SQL command to insert a record """

    def __init__( self, table_name, data ):
        if type( table_name ) != str:
            self.table_name = table_name.name
        else:
            self.table_name = table_name
        self.data = data

    def __str__( self ):
        cols = ', '.join( [ '`%s`' % val for val in self.data.keys() ] )
        vals = ', '.join( [ "'%s'" % str( val ).replace( '\\', '\\\\' ).replace( "'", "\\'" ) for val in self.data.values() ] )
        return 'INSERT INTO `%s` (%s) VALUES (%s);' % ( self.table_name, cols, vals )
