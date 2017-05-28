import unittest

from mygrations.helpers.dotenv import dotenv, DotEnvSyntaxError

# mainly just breakning the tests up a little bit.
# the ability to recognize and parse around quotes inside
# the values does make this a bit more complicated, so it
# makes sense to be in another file anyway
class test_dotenv_parse_line_with_quotes( unittest.TestCase ):

    dotenv = None

    def setUp( self ):

        self.dotenv = dotenv()

    def test_no_lone_quotes_double( self ):

        # a quote character inside the value by itself is invalid
        self.assertRaises( DotEnvSyntaxError, self.dotenv.parse_line, 'name = valu"e', '#' );

    def test_no_lone_quotes_single( self ):

        # a quote character inside the value by itself is invalid
        self.assertRaises( DotEnvSyntaxError, self.dotenv.parse_line, "name = valu'e", '#' );

    def test_empty_single( self ):

        # easy
        self.assertEquals( [ 'db', '' ], self.dotenv.parse_line( "db = ''", '#' ) )

    def test_empty_double( self ):

        # easy
        self.assertEquals( [ 'db', '' ], self.dotenv.parse_line( 'db = ""', '#' ) )

    def test_empty_single_comment( self ):

        # easy
        self.assertEquals( [ 'db', '' ], self.dotenv.parse_line( "db = '' # database name", '#' ) )

    def test_empty_double_comment( self ):

        # easy
        self.assertEquals( [ 'db', '' ], self.dotenv.parse_line( 'db = "" ; database name', ';' ) )

    def test_single_quotes( self ):

        # I shouldn't get the quotes back.  Also white space should
        # be ignored still
        self.assertEquals( [ 'db', 'dijere' ], self.dotenv.parse_line( "db = 'dijere' ", '#' ) )

    def test_double_quotes( self ):

        # I shouldn't get the quotes back.  Also white space should
        # be ignored still
        self.assertEquals( [ 'db', 'dijere' ], self.dotenv.parse_line( 'db = "dijere" ', '#' ) )

    def test_no_closing_quote_single( self ):

        # syntax error if we have an opening quote with no close
        self.assertRaises( DotEnvSyntaxError, self.dotenv.parse_line, "name = 'test", '#' )

    def test_no_closing_quote_double( self ):

        # syntax error if we have an opening quote with no close
        self.assertRaises( DotEnvSyntaxError, self.dotenv.parse_line, 'name = "test', '#' )

    def test_double_quotes_with_comment( self ):

        # comments after the quotes should be ignored (along with whitespace)
        self.assertEquals( [ 'db', 'bob' ], self.dotenv.parse_line( 'db = "bob" ; database name', ';' ) )

    def test_single_quotes_with_comment( self ):

        # comments after the quotes should be ignored (along with whitespace)
        self.assertEquals( [ 'db', 'bob' ], self.dotenv.parse_line( "db = 'bob' \t# database name", '#' ) )

    def test_text_outside_of_double( self ):

        # anything outside of the quotes and before a comment results in a syntax error
        self.assertRaises( DotEnvSyntaxError, self.dotenv.parse_line, 'name = "test" sup # hey', '#' )

    def test_text_outside_of_single( self ):

        # anything outside of the quotes and before a comment results in a syntax error
        self.assertRaises( DotEnvSyntaxError, self.dotenv.parse_line, "name = 'test' sup ; hey", ';' )

    def test_allow_ending_semicolon( self ):

        # anything outside of the quotes and before a comment results in a syntax error
        # except allow to end the line with a semi-colon.
        self.assertEquals( [ 'name', 'test' ], self.dotenv.parse_line( "name = 'test';", '#' ) )

    def test_escaped_single_quote( self ):

        # quotes can be escaped inside quotes
        self.assertEquals( [ 'db', "asdf'qwerty'" ], self.dotenv.parse_line( "db = 'asdf\\'qwerty\\''", '#' ) )

    def test_escaped_double_quote( self ):

        # quotes can be escaped inside quotes
        self.assertEquals( [ 'db', 'asdf"qwerty"' ], self.dotenv.parse_line( 'db = "asdf\\"qwerty\\""', '#' ) )

    def test_preserve_other_slashes( self ):

        # other slashes are left alone
        self.assertEquals( [ 'db', 'asdf\\bob' ], self.dotenv.parse_line( 'db = "asdf\\bob"', '#' ) )

    def test_double_quote_in_single_quote( self ):

        # double quote inside single quotes are just regular characters
        self.assertEquals( [ 'db', 'asdf"bob' ], self.dotenv.parse_line( "db = 'asdf\"bob'", '#' ) )

    def test_single_quote_in_double_quote( self ):

        # single quote inside double quotes are just regular characters
        self.assertEquals( [ 'db', "asdf'bob" ], self.dotenv.parse_line( 'db = "asdf\'bob"', '#' ) )
