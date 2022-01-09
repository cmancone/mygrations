import unittest

from mygrations.helpers.dotenv import dotenv, DotEnvSyntaxError
import io
import tempfile
class DotEnvTest(unittest.TestCase):

    dotenv = None
    test_string = 'test string'

    def setUp(self):

        self.dotenv = dotenv()

    # get_contents should accept a number of parameters.
    # It should accept a stringIO wrapper
    def test_get_contents_stringIO(self):

        self.assertEquals(self.test_string, self.dotenv.get_contents(io.StringIO(self.test_string)))

    # it should also accept an actual string
    def test_get_contents_string(self):

        self.assertEquals(self.test_string, self.dotenv.get_contents(self.test_string))

    # as well as a more general file pointer
    def test_get_contents_fp(self):

        fp = tempfile.TemporaryFile()
        fp.write(self.test_string.encode(encoding='UTF-8'))
        fp.seek(0)
        self.assertEquals(self.test_string, self.dotenv.get_contents(fp))
        fp.close()

    # it should also accept a filename
    def test_get_contents_filename(self):

        filename = '%s/unit_mygrations_dotenv' % tempfile.gettempdir()
        fp = open(filename, 'w')
        fp.write(self.test_string)
        fp.close()

        self.assertEquals(self.test_string, self.dotenv.get_contents(filename))

    def test_json(self):

        # it should detect json and parse it as such
        parsed = self.dotenv.parse('{ "key": "value",\n "name": "bob" }')

        self.assertEquals({'key': 'value', 'name': 'bob'}, parsed)

    def test_dont_interrupt_syntax_error(self):

        # a syntax error from parse_line should not be stopped
        self.assertRaises(DotEnvSyntaxError, self.dotenv.parse, 'name')

    def test_parse_each_line(self):

        # otherwise each line should be parsed
        parsed = self.dotenv.parse('key = value\nname = bob #sup')

        self.assertEquals({'key': 'value', 'name': 'bob'}, parsed)

    def test_parse_skip_empty(self):

        # some whitespace checks and a few parts just because
        parsed = self.dotenv.parse('key = value\n\n\n\n   name = "bob" # sup\n another = "test\\"value"#okay')

        self.assertEquals({'key': 'value', 'name': 'bob', 'another': 'test"value'}, parsed)

    def test_opening_comment(self):

        self.assertEquals([False, False], self.dotenv.parse_line('# name = test', '#'))

    def test_opening_comment_with_space(self):

        # white space is stripped first, so it still starts with a comment if it has spaces
        self.assertEquals([False, False], self.dotenv.parse_line(' # name = test', '#'))

    def test_any_comment_charater(self):

        # our comment character should be respected
        self.assertEquals([False, False], self.dotenv.parse_line('; name = test', ';'))

    def test_multi_character_comment(self):

        # and it is allowed to be more than one character long
        self.assertEquals([False, False], self.dotenv.parse_line('weirdcomment name = test', 'weirdcomment'))

    def test_ignore_empty_lines(self):

        # empty lines (which includes lines with all white space) are ignored
        self.assertEquals([False, False], self.dotenv.parse_line('  ', '#'))

    def test_invalid_format(self):

        # supported format is something like name = value or name: value
        # if neither of the separators is present then we should get a syntax error
        self.assertRaises(DotEnvSyntaxError, self.dotenv.parse_line, 'sup', '#')

    def test_empty_value_equal(self):

        # empty values are allowed
        self.assertEquals(['key', ''], self.dotenv.parse_line('key=', '#'))

    def test_empty_value_colon(self):

        # colons act exactly the same way
        self.assertEquals(['key', ''], self.dotenv.parse_line('key:', '#'))

    def test_empty_value_equal_spaces(self):

        # and spaces are ignored
        self.assertEquals(['key', ''], self.dotenv.parse_line(" key \t=\t  ", '#'))

    def test_empty_value_equal_colon(self):

        # and spaces are ignored
        self.assertEquals(['key', ''], self.dotenv.parse_line(" key \t:\t  ", '#'))

    def test_value_no_quotes_equal(self):

        # a value without quotes should be easy
        self.assertEquals(['key', 'asdf'], self.dotenv.parse_line("key=asdf", '#'))

    def test_value_no_quotes_colon(self):

        # a value without quotes should be easy
        self.assertEquals(['key', 'asdf'], self.dotenv.parse_line("key:asdf", '#'))

    def test_value_no_quotes_equal_spaces(self):

        # spaces are still ignored at the beginning/end of a part
        self.assertEquals(['key', 'asdf bob'], self.dotenv.parse_line("key= asdf bob  \t", '#'))

    def test_value_no_quotes_equal_colon(self):

        # spaces are still ignored at the beginning/end of a part
        self.assertEquals(['key', 'asdf bob'], self.dotenv.parse_line("key : asdf bob  \t", '#'))

    def test_value_no_quotes_equal_comment(self):

        # and comments at the end are ignored (including spaces before comments)
        self.assertEquals(['key', 'asdf bob'], self.dotenv.parse_line("key = asdf bob  \t# a comment", '#'))

    def test_value_no_quotes_equal_colon(self):

        # and comments at the end are ignored (including spaces before comments)
        self.assertEquals(['key', 'asdf bob'], self.dotenv.parse_line("key : asdf bob  \t; a comment", ';'))

    def test_no_lone_quotes_double(self):

        # a quote character inside the value by itself is invalid
        self.assertRaises(DotEnvSyntaxError, self.dotenv.parse_line, 'name = valu"e', '#')

    def test_no_lone_quotes_single(self):

        # a quote character inside the value by itself is invalid
        self.assertRaises(DotEnvSyntaxError, self.dotenv.parse_line, "name = valu'e", '#')

    def test_empty_single(self):

        # easy
        self.assertEquals(['db', ''], self.dotenv.parse_line("db = ''", '#'))

    def test_empty_double(self):

        # easy
        self.assertEquals(['db', ''], self.dotenv.parse_line('db = ""', '#'))

    def test_empty_single_comment(self):

        # easy
        self.assertEquals(['db', ''], self.dotenv.parse_line("db = '' # database name", '#'))

    def test_empty_double_comment(self):

        # easy
        self.assertEquals(['db', ''], self.dotenv.parse_line('db = "" ; database name', ';'))

    def test_single_quotes(self):

        # I shouldn't get the quotes back.  Also white space should
        # be ignored still
        self.assertEquals(['db', 'dijere'], self.dotenv.parse_line("db = 'dijere' ", '#'))

    def test_double_quotes(self):

        # I shouldn't get the quotes back.  Also white space should
        # be ignored still
        self.assertEquals(['db', 'dijere'], self.dotenv.parse_line('db = "dijere" ', '#'))

    def test_no_closing_quote_single(self):

        # syntax error if we have an opening quote with no close
        self.assertRaises(DotEnvSyntaxError, self.dotenv.parse_line, "name = 'test", '#')

    def test_no_closing_quote_double(self):

        # syntax error if we have an opening quote with no close
        self.assertRaises(DotEnvSyntaxError, self.dotenv.parse_line, 'name = "test', '#')

    def test_double_quotes_with_comment(self):

        # comments after the quotes should be ignored (along with whitespace)
        self.assertEquals(['db', 'bob'], self.dotenv.parse_line('db = "bob" ; database name', ';'))

    def test_single_quotes_with_comment(self):

        # comments after the quotes should be ignored (along with whitespace)
        self.assertEquals(['db', 'bob'], self.dotenv.parse_line("db = 'bob' \t# database name", '#'))

    def test_text_outside_of_double(self):

        # anything outside of the quotes and before a comment results in a syntax error
        self.assertRaises(DotEnvSyntaxError, self.dotenv.parse_line, 'name = "test" sup # hey', '#')

    def test_text_outside_of_single(self):

        # anything outside of the quotes and before a comment results in a syntax error
        self.assertRaises(DotEnvSyntaxError, self.dotenv.parse_line, "name = 'test' sup ; hey", ';')

    def test_allow_ending_semicolon(self):

        # anything outside of the quotes and before a comment results in a syntax error
        # except allow to end the line with a semi-colon.
        self.assertEquals(['name', 'test'], self.dotenv.parse_line("name = 'test';", '#'))

    def test_escaped_single_quote(self):

        # quotes can be escaped inside quotes
        self.assertEquals(['db', "asdf'qwerty'"], self.dotenv.parse_line("db = 'asdf\\'qwerty\\''", '#'))

    def test_escaped_double_quote(self):

        # quotes can be escaped inside quotes
        self.assertEquals(['db', 'asdf"qwerty"'], self.dotenv.parse_line('db = "asdf\\"qwerty\\""', '#'))

    def test_preserve_other_slashes(self):

        # other slashes are left alone
        self.assertEquals(['db', 'asdf\\bob'], self.dotenv.parse_line('db = "asdf\\bob"', '#'))

    def test_double_quote_in_single_quote(self):

        # double quote inside single quotes are just regular characters
        self.assertEquals(['db', 'asdf"bob'], self.dotenv.parse_line("db = 'asdf\"bob'", '#'))

    def test_single_quote_in_double_quote(self):

        # single quote inside double quotes are just regular characters
        self.assertEquals(['db', "asdf'bob"], self.dotenv.parse_line('db = "asdf\'bob"', '#'))
