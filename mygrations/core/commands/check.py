from .base import Base
from mygrations.formats.mysql.file_reader.database import Database as DatabaseParser
from mygrations.formats.mysql.mygrations.mygration import Mygration


def execute(options, print_results=True):
    obj = Check(options)
    return obj.execute(print_results=print_results)


class Check(Base):
    def execute(self, print_results=True):
        files_database = DatabaseParser(self.get_sql_files())

        errors = []
        warnings = []
        if files_database.errors:
            errors.append("Errors found in *.sql files:")
            errors.extend(files_database.errors)

        if files_database.warnings:
            warnings.append("Warnings found in *.sql files:")
            warnings.extend(files_database.warnings)

        if print_results:
            if not errors and not warnings:
                print("No problems found")
            else:
                if errors:
                    print("\n".join(errors))
                if warnings:
                    print("\n".join(warnings))
        return (errors, True if not len(errors) else False)
