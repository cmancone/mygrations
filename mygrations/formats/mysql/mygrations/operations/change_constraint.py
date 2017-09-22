class change_constraint:
    """ Generates a partial SQL command to change a foreign key in a table """

    def __init__( self, constraint ):
        self.constraint = constraint

    def __str__( self ):
        return 'DROP FOREIGN KEY %s, ADD %s' % ( self.constraint.name, str( self.constraint ) )
