import io, os
from .comment_parser import CommentParser
from .create_parser import CreateParser
from .insert_parser import InsertParser
class Reader:
    def __init__(self):

        self._tables = {}
        self._rows = {}
        self._global_errors = []
        self._global_warnings = []
        self._parsing_errors = []
        self._parsing_warnings = []
        self._schema_errors = []
        self._schema_warnings = []
        self._matched = False

    @property
    def matched(self):
        """ Public getter.  Returns whether or not the content was successfully parsed

        :returns: Whether or not parsing was successful
        :rtype: bool
        """
        return self._matched

    @property
    def parsing_errors(self):
        """ Public getter.  Returns a list of parsing errors

        :returns: A list of parsing errors
        :rtype: list
        """
        return [] if self._parsing_errors is None else self._parsing_errors

    @property
    def parsing_warnings(self):
        """ Public getter.  Returns a list of parsing/table warnings

        :returns: A list of parsing/table warnings
        :rtype: list
        """
        return [] if self._parsing_warnings is None else self._parsing_warnings

    @property
    def schema_errors(self):
        """ Public getter.  Returns a list of schema errors

        :returns: A list of schema errors
        :rtype: list
        """
        return [] if self._schema_errors is None else self._schema_errors

    @property
    def schema_warnings(self):
        """ Public getter.  Returns a list of schema warnings

        :returns: A list of schema warnings
        :rtype: list
        """
        return [] if self._schema_warnings is None else self._schema_warnings

    @property
    def global_errors(self):
        """ Public getter.  Returns a list of schema errors

        :returns: A list of schema errors
        :rtype: list
        """
        return [] if self._global_errors is None else self._global_errors

    @property
    def global_warnings(self):
        """ Public getter.  Returns a list of schema warnings

        :returns: A list of schema warnings
        :rtype: list
        """
        return [] if self._global_warnings is None else self._global_warnings

    @property
    def tables(self):
        """ Public getter.  Returns a list of table definitions

        :returns: A list of table definitions
        :rtype: dict[mygrations.formats.mysql.definitions.table]
        """
        return self._tables

    @property
    def rows(self):
        """ Public getter.  Returns a dictionary containing a lists of rows by table name

        :returns: A dictionary containing list of rows by table name
        :rtype: {table_name: [mygrations.formats.mysql.defintions.row]}
        """
        return self._rows

    """ Helper that returns info about the current filename (if present) for error messages

    :returns: Part of an error message
    :rtype: string
    """

    def _filename_notice(self):

        if self.filename:
            return ' in file %s' % self.filename

        return ''

    """ Reads the file, if necessary

    Reader is a bit more flexible than the other parsers.  It can accept a filename,
    file-like object, or a string.  This method handles that flexibility, taking
    the input from the _parse method and extracting the actual contents no matter
    what was passed in.

    :returns: The data to parse
    :rtype: string
    """

    def _unpack(self, filename):

        # be flexible about what we accept
        # file pointer
        self.filename = ''
        if isinstance(filename, io.IOBase):
            contents = filename.read()

        # and an actual string
        elif isinstance(filename, str):

            # which could be a filename
            if os.path.isfile(filename):
                self.filename = filename
                fp = open(filename, 'r')
                contents = fp.read()
                fp.close()
            else:
                contents = filename

        else:
            raise ValueError(
                "Unknown type for filename: must be an ascii string, a filename, file pointer, or StringIO"
            )

        return contents

    """ Main parsing loop: attempts to find create, insert, and comments in the SQL string
    """

    def parse(self, filename):

        data = self._unpack(filename)

        # okay then!  This is our main parsing loop.
        c = 0
        while data:
            c += 1
            if c > 10000:
                raise ValueError("Exceeded max parse depth")

            # never hurts
            data = data.strip()

            # now we are looking for one of three things:
            # comment, create, insert
            if data[:2] == '--' or data[:2] == '/*' or data[0] == '#':
                parser = CommentParser()
                data = parser.parse(data)

            elif data[:6].lower() == 'create':
                parser = CreateParser()
                data = parser.parse(data)
                self._tables[parser.name] = parser

            elif data[:6].lower() == 'insert':
                parser = InsertParser()
                data = parser.parse(data)
                if not parser.table in self._rows:
                    self._rows[parser.table] = []

                self._rows[parser.table].append(parser)

            else:
                if self._global_errors is None:
                    self._global_errors = []
                self._global_errors.append("Unrecognized MySQL command: %s%s" % (data, self._filename_notice()))
                return data

        self._matched = True
        return data
