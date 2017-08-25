import io, os
from .comment_parser import comment_parser
from .create_parser import create_parser
from .insert_parser import insert_parser

class reader( object ):

    def __init__( self ):

        self.tables = {}
        self.rows = {}
        self.errors = []
        self.warnings = []
        self.matched = False

    """ Helper that returns info about the current filename (if present) for error messages

    :returns: Part of an error message
    :rtype: string
    """
    def _filename_notice( self ):

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
    def _unpack( self, filename ):

        # be flexible about what we accept
        # file pointer
        self.filename = ''
        if isinstance( filename, io.IOBase ):
            contents = filename.read()

        # and an actual string
        elif isinstance( filename, str ):

            # which could be a filename
            if os.path.isfile( filename ):
                self.filename = filename
                fp = open( filename, 'r' )
                contents = fp.read()
                fp.close()
            else:
                contents = filename

        else:
            raise ValueError( "Unknown type for filename: must be an ascii string, a filename, file pointer, or StringIO" )

        return contents

    """ Main parsing loop: attempts to find create, insert, and comments in the SQL string
    """
    def parse( self, filename ):

        data = self._unpack( filename )

        # okay then!  This is our main parsing loop.
        c = 0;
        while data:
            c += 1
            if c > 10000:
                raise ValueError( "Exceeded max parse depth" )

            # never hurts
            data = data.strip()

            # now we are looking for one of three things:
            # comment, create, insert
            if data[:2] == '--' or data[:2] == '/*' or data[0] == '#':
                try:
                    parser = comment_parser();
                    data = parser.parse( data )
                except SyntaxError as e:
                    self.errors.append( 'Parsing error: %s%s' % ( str(e), self._filename_notice() ) )

            elif data[:6].lower() == 'create':
                parser = create_parser()
                data = parser.parse( data )
                self.tables[parser.name] = parser

            elif data[:6].lower() == 'insert':
                parser = insert_parser()
                data = parser.parse( data )
                if not parser.table in self.rows:
                    self.rows[parser.table] = []

                self.rows[parser.table].append( parser )

            else:
                raise ValueError( "Unrecognized MySQL command: %s" % data )

        self.matched = True
        return data
