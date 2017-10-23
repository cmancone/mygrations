import MySQLdb
import glob
import os

from mygrations.helpers.dotenv import dotenv
from mygrations.helpers.db_credentials import db_credentials
from mygrations.formats.mysql.file_reader.database import database as database_parser
from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.formats.mysql.mygrations.mygration import mygration

def execute( options ):

    obj = import_files( options )
    obj.execute()

class import_files( object ):

    credentials = {}
    config = {}

    def __init__( self, options ):

        self.options = options

        if not 'env' in self.options:
            raise ValueError( 'Missing "env" in options for commands.import_files' )

        if not 'config' in self.options:
            raise ValueError( 'Missing "config" in options for commands.import_files' )

        # load up the mygration configuration (which includes the path to the files we will import)
        self.config = dotenv( self.options['config'] )

        # and load up the database credentials
        self.credentials = db_credentials( self.options['env'], self.config )

        if not 'files_directory' in self.config:
            raise ValueError( 'Missing files_directory configuration setting in configuration file' )

    def execute( self ):

        files_database = database_parser( self.config['files_directory'] )

        # any errors or warnings?
        if files_database.errors:
            print( 'Errors found in *.sql files' )
            for error in files_database.errors:
                print( error )

            return False

        # use the credentials to load up a database connection
        conn = MySQLdb.connect( **self.credentials )

        live_database = database_reader( conn )

        mygrate = mygration( files_database, live_database )
        if mygrate.errors_1215:
            print( '1215 Errors encountered' )
            for error in mygrate.errors_1215:
                print( error )

        else:
            for op in mygrate.operations:
                print( op )
