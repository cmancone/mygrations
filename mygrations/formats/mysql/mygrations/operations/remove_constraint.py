class remove_constraint:
    """ Generates a partial SQL command to drop a foreign key from a table """

    def __init__( self, constraint ):
        self.constraint = constraint

    def __str__( self ):
        return 'DROP FOREIGN KEY %s' % (self.constraint.name)
