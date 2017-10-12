class remove_table:
    """ Generates an SQL command to drop a table """

    def __init__( self, table_name ):
        if type( table_name ) != str:
            self.table_name = table_name.name
        else:
            self.table_name = table_name

    def __str__( self ):
        return 'DROP TABLE %s;' % self.table_name
