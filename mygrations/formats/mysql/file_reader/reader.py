import io, os
from .comment_parser import comment_parser
from .create_parser import create_parser
from .insert_parser import insert_parser

class reader( object ):

    contents = ''
    tables = []
    records = []

    def __init__( self, filename ):

        self.tables = []
        self.records = []

        # be flexible about what we accept
        # file pointer
        if isinstance( filename, io.IOBase ):
            self.contents = filename.read()

        # and an actual string
        elif isinstance( filename, str ):

            # which could be a filename
            if os.path.isfile( filename ):
                fp = open( filename, 'r' )
                self.contents = fp.read()
                fp.close()
            else:
                self.contents = filename

        else:
            raise ValueError( "Unknown type for filename: must be an ascii string, a filename, file pointer, or StringIO" )

        ( self.tables, self.records ) = self.parse( self.contents )

    def parse( self, data ):

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
                parser_class = comment_parser

            elif data[:6].lower() == 'create':
                parser_class = create_parser

            elif data[:6].lower() == 'insert':
                parser_class = insert_parser

            else:
                raise ValueError( "Unrecognized MySQL command: %s" % data )

            # now load up our parser
            parser = parser_class()
            data = parser.parse( data )

        return ( '', '' )
