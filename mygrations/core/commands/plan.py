from .base import base
from mygrations.formats.mysql.file_reader.database import database as database_parser
from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.formats.mysql.mygrations.mygration import mygration
from mygrations.formats.mysql.mygrations.row_mygration import row_mygration
from mygrations.drivers.mysqldb.mysqldb import mysqldb
from mygrations.formats.mysql.mygrations.operations.disable_checks import disable_checks
from mygrations.formats.mysql.mygrations.operations.enable_checks import enable_checks

def execute( options ):

    obj = plan( options )
    obj.execute()

class plan( base ):

    def execute( self ):

        files_database = database_parser( self.config['files_directory'] )

        # any errors or warnings?
        if files_database.errors:
            print( 'Errors found in *.sql files' )
            for error in files_database.errors:
                print( error )

            return False

        # use the credentials to load up a database connection
        live_database = database_reader( mysqldb( self.credentials ) )

        # we have to tell the live database to load records
        # for any tables we are tracking records for.
        # We use the "files" database as the "truth" because
        # just about any database can have records, but
        # that doesn't mean we want to track them.  We only
        # track them if the file has rows.
        for table in files_database.tables.values():
            if not table.tracking_rows:
                continue

            if not table.name in live_database.tables:
                continue

            live_database.read_rows( table )

        mygrate = mygration( files_database, live_database, False )
        if mygrate.errors_1215:
            print( '1215 Errors encountered' )
            for error in mygrate.errors_1215:
                print( error )
            return False

        ops = []
        if mygrate.operations:
            ops.extend( mygrate.operations )

        rows = row_mygration( files_database, live_database )
        if rows.operations:
            ops.extend( rows.operations )

        if not ops:
            return True

        print( disable_checks() )
        for op in ops:
            print( op )
        print( enable_checks() )
