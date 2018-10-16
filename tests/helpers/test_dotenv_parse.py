import unittest

from mygrations.helpers.dotenv import dotenv, DotEnvSyntaxError
# this does very little really, other than  run .parse_line on each line.
# parse_line is thoroughly tested, so we don't need to do much.
class test_dotenv_parse(unittest.TestCase):

    dotenv = None

    def setUp(self):

        self.dotenv = dotenv()

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
