from .base import Base
from mygrations.formats.mysql.file_reader.database import Database as DatabaseParser
from mygrations.formats.mysql.mygrations.mygration import Mygration


def execute(options):
    obj = Check(options)
    obj.execute()


class Check(Base):
    def execute(self):
        files_database = DatabaseParser(self.config['files_directory'])

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
