import unittest

from mygrations.helpers.dotenv import dotenv, DotEnvSyntaxError

class test_dotenv_parse_line( unittest.TestCase ):

    dotenv = None

    def setUp( self ):

        self.dotenv = dotenv()

    def test_opening_comment( self ):

        self.assertEquals( [ False, False ], self.dotenv.parse_line( '# name = test', '#' ) )

    def test_opening_comment_with_space( self ):

        # white space is stripped first, so it still starts with a comment if it has spaces
        self.assertEquals( [ False, False ], self.dotenv.parse_line( ' # name = test', '#' ) )

    def test_any_comment_charater( self ):

        # our comment character should be respected
        self.assertEquals( [ False, False ], self.dotenv.parse_line( '; name = test', ';' ) )

    def test_multi_character_comment( self ):

        # and it is allowed to be more than one character long
        self.assertEquals( [ False, False ], self.dotenv.parse_line( 'weirdcomment name = test', 'weirdcomment' ) )

    def test_ignore_empty_lines( self ):

        # empty lines (which includes lines with all white space) are ignored
        self.assertEquals( [ False, False ], self.dotenv.parse_line( '  ', '#' ) )

    def test_invalid_format( self ):

        # supported format is something like name = value or name: value
        # if neither of the separators is present then we should get a syntax error
        self.assertRaises( DotEnvSyntaxError, self.dotenv.parse_line, 'sup', '#' );

    def test_empty_value_equal( self ):

        # empty values are allowed
        self.assertEquals( [ 'key', '' ], self.dotenv.parse_line( 'key=', '#' ) )

    def test_empty_value_colon( self ):

        # colons act exactly the same way
        self.assertEquals( [ 'key', '' ], self.dotenv.parse_line( 'key:', '#' ) )

    def test_empty_value_equal_spaces( self ):

        # and spaces are ignored
        self.assertEquals( [ 'key', '' ], self.dotenv.parse_line( " key \t=\t  ", '#' ) )

    def test_empty_value_equal_colon( self ):

        # and spaces are ignored
        self.assertEquals( [ 'key', '' ], self.dotenv.parse_line( " key \t:\t  ", '#' ) )

    def test_value_no_quotes_equal( self ):

        # a value without quotes should be easy
        self.assertEquals( [ 'key', 'asdf' ], self.dotenv.parse_line( "key=asdf", '#' ) )

    def test_value_no_quotes_colon( self ):

        # a value without quotes should be easy
        self.assertEquals( [ 'key', 'asdf' ], self.dotenv.parse_line( "key:asdf", '#' ) )

    def test_value_no_quotes_equal_spaces( self ):

        # spaces are still ignored at the beginning/end of a part
        self.assertEquals( [ 'key', 'asdf bob' ], self.dotenv.parse_line( "key= asdf bob  \t", '#' ) )

    def test_value_no_quotes_equal_colon( self ):

        # spaces are still ignored at the beginning/end of a part
        self.assertEquals( [ 'key', 'asdf bob' ], self.dotenv.parse_line( "key : asdf bob  \t", '#' ) )

    def test_value_no_quotes_equal_comment( self ):

        # and comments at the end are ignored (including spaces before comments)
        self.assertEquals( [ 'key', 'asdf bob' ], self.dotenv.parse_line( "key = asdf bob  \t# a comment", '#' ) )

    def test_value_no_quotes_equal_colon( self ):

        # and comments at the end are ignored (including spaces before comments)
        self.assertEquals( [ 'key', 'asdf bob' ], self.dotenv.parse_line( "key : asdf bob  \t; a comment", ';' ) )
