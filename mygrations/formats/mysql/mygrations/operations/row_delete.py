class row_delete:
    """ Generates an SQL command to delete a record """

    def __init__( self, table_name, row_id ):
        if type( table_name ) != str:
            self.table_name = table_name.name
        else:
            self.table_name = table_name
        self.row_id = row_id

    def __str__( self ):
        return 'DELETE FROM `%s` WHERE id=%s;' % (self.table_name, self.row_id)
