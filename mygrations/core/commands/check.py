from .base import Base
from mygrations.formats.mysql.file_reader.database import Database as DatabaseParser
from mygrations.formats.mysql.mygrations.mygration import Mygration
def execute(options):
    obj = Check(options)
    obj.execute()
class Check(Base):
    def execute(self):
        files_database = DatabaseParser(self.get_sql_files())

        # any errors or warnings?
        errors = False
        if files_database.errors:
            print('Errors found in *.sql files:')
            errors = True
            for error in files_database.errors:
                print(error)

        warnings = files_database.warnings
        if warnings:
            print('Warnings found in *.sql files:')
            errors = True
            for warning in warnings:
                print(warning)

        if not errors:
            print("No problems found")
