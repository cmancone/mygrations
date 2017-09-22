class add_constraint:
    """ Generates a partial SQL command to add a FK to a table """

    def __init__( self, constraint ):
        self.constraint = constraint

    def __str__( self ):
        return 'ADD %s' % str( self.constraint )
