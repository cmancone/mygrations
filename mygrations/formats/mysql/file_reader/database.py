import os
import glob

from .reader import reader

class database( object ):

    def __init__( self, strings ):
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

        if isinstance( strings, str ):
            strings = [ strings ]

        for string in strings:
            self.process( string )

    def process( self, string ):
        """ Processes a string.

        Strings can be either SQL to parse, the location of an SQL file, or a directory containing SQL files

        :param string: A string containing one of the above
        :type string: string
        """

        if os.path.isdir( string ):
            self._process_directory( string )
        elif os.path.isfile( string ):
            self._read( string )
        else:
            self._read( string )

    def _process_directory( directory ):
        """ Processes a directory.

        Finds all SQL files in the directory and calls `_read()` on them,
        which results in the file being parsed and its tables/rows added to the
        record of database tables/rows.

        :param string: A string containing one of the above
        :type string: string
        """

        if directory[-1] != os.sep:
            directory += os.sep

        for filename in glob.glob( '%s*.sql' % directory ):
            self._read( filename )

    def _read( contents ):
        """ Processes a file or string of SQL.

        Creates a reader object (which accepts files or a string of SQL)
        to parse its input and stores the tables/rows in the database
        object.

        :param contents: A string containing a filename or SQL
        :type contents: string
        """

        try:
            contents = reader( filename )
        except ValueError as e:
            print( "Error in file %s: %s" % ( filename, e ) )

