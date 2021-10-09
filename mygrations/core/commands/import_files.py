from .base import Base
from mygrations.formats.mysql.file_reader.database import Database as DatabaseParser
from mygrations.formats.mysql.db_reader.database import Database as DatabaseReader
from mygrations.formats.mysql.mygrations.mygration import Mygration
from mygrations.drivers.mysqldb.mysqldb import mysqldb
def execute(options):

    obj = ImportFiles(options)
    obj.execute()
class ImportFiles(base):
    def execute(self):

        files_database = DatabaseParser(self.config['files_directory'])

        # any errors or warnings?
        if files_database.errors:
            print('Errors found in *.sql files')
            for error in files_database.errors:
                print(error)

            return False

        # use the credentials to load up a database connection
        live_database = DatabaseReader(mysqldb(self.credentials))

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

            live_database.read_rows(table)

        mygrate = Mygration(files_database, live_database)
        if mygrate.errors_1215:
            print('1215 Errors encountered')
            for error in mygrate.errors_1215:
                print(error)

        else:
            for op in mygrate.operations:
                live_database.apply_to_source(op)
