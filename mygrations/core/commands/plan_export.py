from collections import OrderedDict

from .base import base
from mygrations.formats.mysql.file_reader.database import database as database_parser
from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.formats.mysql.mygrations.mygration import mygration
from mygrations.formats.mysql.mygrations.row_mygration import row_mygration
from mygrations.formats.mysql.mygrations.operations.row_insert import row_insert
from mygrations.drivers.mysqldb.mysqldb import mysqldb

def execute( options ):

    obj = plan_export( options )
    obj.execute()

class plan_export( base ):

    def execute( self ):

        files_database = database_parser( self.config['files_directory'] )

        # use the credentials to load up a database connection
        live_database = database_reader( mysqldb( self.credentials ) )

        # we aren't outputting operations.  Instead we just need to know what tables
        # have changed (either structure or records).  The easiest (and slightly hack)
        # way to do that is to simply run an actual mygration and grab out the names
        # of the tables that have changed.  Cheating, I know
        self.modified_tables = {}
        mygrate = mygration( live_database, files_database, False )
        if mygrate.operations:
            for op in mygrate.operations:
                self.modified_tables[op.table_name] = True

        # we have to tell the live database to load records
        # for any tables we are tracking records for, according
        # to the files database.
        for table in files_database.tables.values():
            if not table.tracking_rows:
                continue
            if not table.name in live_database.tables:
                continue
            live_database.read_rows( table )

        rows = row_mygration( live_database, files_database )
        if rows.operations:
            for op in rows.operations:
                self.modified_tables[op.table_name] = True

        for table_name in self.modified_tables.keys():
            print( '\033[1;33m\033[41m%s\033[0m' % table_name )
            table = live_database.tables[table_name]
            print( table.nice() )

            if table.tracking_rows:
                print( '\n' )
                for row in table.rows.values():
                    print( row_insert( table.name, row ) )
