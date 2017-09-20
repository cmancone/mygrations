class change_column:
    """ Generates a partial SQL command to change a column in a table """

    def __init__( self, column ):
        self.column = column

    def __str__( self ):
        return 'CHANGE %s %s' % (self.column.name, self.column)
