class remove_table:
    """ Generates an SQL command to drop a table """

    def __init__( self, table ):
        self.table = table

    def __str__( self ):
        return 'DROP TABLE %s;' % self.table.name
