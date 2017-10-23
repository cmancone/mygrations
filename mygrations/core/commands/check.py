import MySQLdb

from .base import base
from mygrations.formats.mysql.file_reader.database import database as database_parser
from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.formats.mysql.mygrations.mygration import mygration

def execute( options ):

    obj = check( options )
    obj.execute()

class check( base ):

    def execute( self ):
        files_database = database_parser( self.config['files_directory'] )

        # any errors or warnings?
        if files_database.errors:
            print( 'Errors found in *.sql files' )
            for error in files_database.errors:
                print( error )
            return False

        errors_1215 = files_database.errors_1215
        if errors_1215:
            print( '1215 Errors encountered' )
            for error in errors_1215:
                print( error )
            return False

        print( "No problems found" )
