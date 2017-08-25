from .reader import reader

class database( object ):

    def __init__( self, files_directory ):

        self.files_directory = files_directory

        # and make sure that ends in a slash
        if self.files_directory[-1] != os.sep:
            self.files_directory = '%s%s' % ( self.files_directory, os.sep )

        for filename in glob.glob( '%s*.sql' % self.files_directory ):

            try:
                contents = reader( filename )
            except ValueError as e:
                print( "Error in file %s: %s" % ( filename, e ) )
