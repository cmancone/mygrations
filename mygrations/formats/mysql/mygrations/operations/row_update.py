class row_update:
    """ Generates an SQL command to update a record """

    def __init__( self, table_name, data ):
        if 'id' not in data:
            raise KeyError( 'Missing `id` column needed for update' )

        if type( table_name ) != str:
            self.table_name = table_name.name
        else:
            self.table_name = table_name
        self.data = data

    def __str__( self ):
        updates = ', '.join( [ "`%s`='%s'" % ( key, val ) for ( key, val ) in self.data.items() if key != 'id' ] )
        return 'UPDATE `%s` SET %s WHERE id=%s' % ( self.table_name, updates, self.data['id'] )
