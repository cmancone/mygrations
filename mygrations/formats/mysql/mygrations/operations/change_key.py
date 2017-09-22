class change_key:
    """ Generates a partial SQL command to change a key in a table """

    def __init__( self, key ):
        self.key = key

    def __str__( self ):
        return 'DROP KEY `%s`, ADD KEY %s' % ( self.key.name, str( self.key ) )
