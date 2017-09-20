class add_column:
    """ Generates a partial SQL command to add a column to a table """

    def __init__( self, column ):
        self.column = column

    def __str__( self ):
        return 'ADD %s' % self.column
