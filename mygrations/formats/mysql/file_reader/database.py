import os
import glob
from .reader import Reader
from mygrations.formats.mysql.definitions.database import Database as BaseDatabase
class Database(BaseDatabase):
    def __init__(self, strings):
        """ Constructor.  Accepts a string or list of strings with different possible contents

        Strings can be one of the following:

        ==================  ====================
        Type                Value
        ==================  ====================
        string              SQL to parse
        string              A filename to read and to parse as SQL
        string              A directory name to search for .sql files, parsing each one
        list                A list of strings, with each element corresponding to any of the above
        ==================  ====================

        :param strings: A string or list of strings corresponding to one of the allowed input types
        :type strings: string|list
        """

        self._tables = {}
        self._rows = {}
        self._global_errors = []
        self._global_warnings = []

        if isinstance(strings, str):
            strings = [strings]

        for string in strings:
            self.process(string)

        self._combine_tables_and_rows()

    def process(self, string):
        """ Processes a string.

        Strings can be either SQL to parse, the location of an SQL file, or a directory containing SQL files

        :param string: A string containing one of the above
        :type string: string
        """

        if os.path.isdir(string):
            self._process_directory(string)
        elif os.path.isfile(string):
            self._read(string)
        else:
            self._read(string)

    def _process_directory(self, directory):
        """ Processes a directory.

        Finds all SQL files in the directory and calls `_read()` on them,
        which results in the file being parsed and its tables/rows added to the
        record of database tables/rows.

        :param string: A string containing one of the above
        :type string: string
        """

        if directory[-1] != os.sep:
            directory += os.sep

        for filename in glob.glob('%s*.sql' % directory):
            self._read(filename)

    def _read(self, contents):
        """ Processes a file or string of SQL.

        Creates a reader object (which accepts files or a string of SQL)
        to parse its input and stores the tables/rows in the database
        object.

        :param contents: A string containing a filename or SQL
        :type contents: string
        """

        try:
            reader = Reader()
            reader.parse(contents)

        except ValueError as e:
            print("Error in file %s: %s" % (contents, e))

        # keep rows and tables separate while we are reading
        for (table_name, table) in reader.tables.items():
            if table.name in self._tables:
                self.errors.append('Found two definitions for table %s' % table.name)
            self._tables[table.name] = table

        self._global_errors.extend(reader._global_errors)
        self._global_warnings.extend(reader._global_warnings)

        for rows_list in reader.rows.values():
            for rows in rows_list:
                if rows.table not in self._rows:
                    self._rows[rows.table] = []
                self._rows[rows.table].append(rows)

    def _combine_tables_and_rows(self):
        for (table_name, rows_list) in self._rows.items():
            if table_name not in self._tables:
                self._global_errors.extend(
                    f"Found rows for table {table_name}, but this table does not exist in the database"
                )
            for rows in rows_list:
                self._tables[table_name].add_rows(rows)
