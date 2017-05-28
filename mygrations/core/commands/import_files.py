from mygrations.helpers.dotenv import dotenv

def execute( options ):

    obj = import_files( options )
    obj.execute()

class import_files( object ):

    options = {}
    env = {}

    def __init__( self, options ):

        self.options = options

        if not 'env' in self.options:
            raise ValueError( 'Missing "env" in options for commands.import_files' )

    def execute( self ):

        # try to read in the .env file
        self.env = dotenv( self.options['env'] )

        print( self.env.parsed )
