from mygrations.helpers.dotenv import dotenv
from mygrations.helpers.db_credentials import db_credentials

def execute( options ):

    obj = import_files( options )
    obj.execute()

class import_files( object ):

    credentials = {}
    options = {}
    env = {}

    def __init__( self, options ):

        self.options = options

        if not 'env' in self.options:
            raise ValueError( 'Missing "env" in options for commands.import_files' )

        if not 'config' in self.options:
            raise ValueError( 'Missing "config" in options for commands.import_files' )

        self.credentials = db_credentials( self.options['env'], self.options['config'] )

        print( self.credentials['hostname'] )
        print( self.credentials['database'] )
        print( self.credentials['username'] )
        print( self.credentials['password'] )

    def execute( self ):

        # try to read in the .env file
        print( 'go!' )
