class alter_table:
    """ Generates an SQL command to alter a table """

    def __init__( self, table ):
        self.table = table
        self._operations = []

    def add_operation( self, operation ):
        self.operations.append( operation )

    def __len__( self ):
        return len(self.operations)

    def __str__( self ):
        return 'ALTER TABLE %s %s' % (self.table, ' '.join( self.operations ))
