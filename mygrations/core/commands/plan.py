from .base import Base
from mygrations.formats.mysql.file_reader.database import Database as DatabaseParser
from mygrations.formats.mysql.db_reader.database import Database as DatabaseReader
from mygrations.formats.mysql.mygrations.mygration import Mygration
from mygrations.formats.mysql.mygrations.row_mygration import RowMygration
from mygrations.formats.mysql.mygrations.operations.disable_checks import DisableChecks
from mygrations.formats.mysql.mygrations.operations.enable_checks import EnableChecks
import sys
def execute(options):

    obj = Plan(options)
    obj.execute()
class Plan(Base):
    needs_cursor = True

    def execute(self):

        commands = self.build_commands()
        print(''.join(['%s\n' % command for command in commands]))

    def build_commands(self):

        files_database = DatabaseParser(self.get_sql_files())

        # any errors or warnings?
        quit_early = False
        if files_database.errors and not self.options['force']:
            print('Errors found in *.sql files', file=sys.stderr)
            quit_early = True
            for error in files_database.errors:
                print(error, file=sys.stderr)

        if quit_early:
            return []

        # use the credentials to load up a database connection
        live_database = DatabaseReader(self.get_driver())

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

        mygrate = Mygration(files_database, live_database, False)

        ops = []
        if mygrate.operations:
            ops.extend(mygrate.operations)

        rows = RowMygration(files_database, live_database)
        if rows.operations:
            ops.extend(rows.operations)

        if not ops:
            return []

        return [
            DisableChecks(),
            *ops,
            EnableChecks(),
        ]
