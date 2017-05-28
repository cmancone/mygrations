import unittest

from mygrations.helpers.dotenv import dotenv
import io
import tempfile

class test_dotenv_get_contents( unittest.TestCase ):

    dotenv = None
    test_string = 'test string'

    def setUp( self ):

        self.dotenv = dotenv()

    # get_contents should accept a number of parameters.
    # It should accept a stringIO wrapper
    def test_get_contents_stringIO( self ):

        self.assertEquals( self.test_string, self.dotenv.get_contents( io.StringIO( self.test_string ) ) )

    # it should also accept an actual string
    def test_get_contents_string( self ):

        self.assertEquals( self.test_string, self.dotenv.get_contents( self.test_string ) )

    # as well as a more general file pointer
    def test_get_contents_fp( self ):

        fp = tempfile.TemporaryFile()
        fp.write( self.test_string.encode( encoding='UTF-8' ) )
        fp.seek( 0 )
        self.assertEquals( self.test_string, self.dotenv.get_contents( fp ) )
        fp.close()

    # it should also accept a filename
    def test_get_contents_filename( self ):

        filename = '%s/unit_mygrations_dotenv' % tempfile.gettempdir()
        fp = open( filename, 'w' )
        fp.write( self.test_string )
        fp.close()

        self.assertEquals( self.test_string, self.dotenv.get_contents( filename ) )
