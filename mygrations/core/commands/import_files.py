import MySQLdb

from .base import base
from mygrations.formats.mysql.file_reader.database import database as database_parser
from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.formats.mysql.mygrations.mygration import mygration

def execute( options ):

    obj = import_files( options )
    obj.execute()

class import_files( base ):

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
                live_database.apply_to_source( op )
