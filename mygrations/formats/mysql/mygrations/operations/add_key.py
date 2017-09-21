class add_key:
    """ Generates a partial SQL command to add a key to a table """

    def __init__( self, key ):
        self.key = key

    def __str__( self ):
        return 'ADD %s' % self.key
