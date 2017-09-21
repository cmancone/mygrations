class remove_key:
    """ Generates a partial SQL command to drop a key from a table """

    def __init__( self, key ):
        self.key = key

    def __str__( self ):
        return 'DROP KEY %s' % (self.key.name)
