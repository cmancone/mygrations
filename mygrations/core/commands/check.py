import MySQLdb

from .base import base
from mygrations.formats.mysql.file_reader.database import database as database_parser
from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.formats.mysql.mygrations.mygration import mygration
def execute(options):

    obj = check(options)
    obj.execute()
class check(base):
    def execute(self):
        files_database = database_parser(self.config['files_directory'])

        # any errors or warnings?
        errors = False
        if files_database.errors:
            print('Errors found in *.sql files')
            errors = True
            for error in files_database.errors:
                print(error)

        errors_1215 = files_database.errors_1215
        if errors_1215:
            print('1215 Errors encountered')
            errors = True
            for error in errors_1215:
                print(error)

        if not errors:
            print("No problems found")
