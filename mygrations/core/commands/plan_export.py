from collections import OrderedDict

from .base import Base
from mygrations.formats.mysql.file_reader.database import Database as DatabaseParser
from mygrations.formats.mysql.db_reader.database import Database as DatabaseReader
from mygrations.formats.mysql.mygrations.mygration import Mygration
from mygrations.formats.mysql.mygrations.row_mygration import RowMygration
from mygrations.formats.mysql.mygrations.operations.row_insert import RowInsert
from mygrations.drivers.mysqldb.mysqldb import mysqldb
def execute(options):

    obj = PlanExport(options)
    obj.execute()
class PlanExport(base):
    def execute(self):

        files_database = DatabaseParser(self.get_sql_files())

        # use the credentials to load up a database connection
        live_database = DatabaseReader(self.get_driver())

        # we aren't outputting operations.  Instead we just need to know what tables
        # have changed (either structure or records).  The easiest (and slightly hack)
        # way to do that is to simply run an actual mygration and grab out the names
        # of the tables that have changed.  Cheating, I know
        self.modified_tables = {}
        mygrate = Mygration(live_database, files_database, False)
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
            live_database.read_rows(table)

        rows = RowMygration(live_database, files_database)
        if rows.operations:
            for op in rows.operations:
                self.modified_tables[op.table_name] = True

        for table_name in self.modified_tables.keys():
            print('\033[1;33m\033[41m%s\033[0m' % table_name)
            table = live_database.tables[table_name]
            print(table.nice())

            if table.tracking_rows:
                print('\n')
                for row in table.rows.values():
                    print(row_insert(table.name, row))
