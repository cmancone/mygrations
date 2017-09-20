class remove_column:
    """ Generates a partial SQL command to remove a column from a table """

    def __init__( self, column ):
        self.column = column

    def __str__( self ):
        return 'DROP %s' % self.column.name
