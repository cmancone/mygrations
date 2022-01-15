import unittest

from mygrations.formats.mysql.file_reader.parsers.type_plain import TypePlain
class TestTypePlain(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypePlain()
        returned = parser.parse("created date NOT NULL DEFAULT 'bob',")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('created', parser._name)
        self.assertEquals('date', parser._column_type)
        self.assertFalse(parser._null)
        self.assertEquals('bob', parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser._parsing_errors))
        self.assertEquals(0, len(parser._parsing_warnings))

    def test_optional_default(self):

        # parse typical insert values
        parser = TypePlain()
        returned = parser.parse("created date")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('created', parser._name)
        self.assertEquals('date', parser._column_type)
        self.assertTrue(parser._null)
        self.assertEquals(None, parser._default)
        self.assertFalse(parser.has_comma)
        self.assertEquals(0, len(parser._parsing_errors))
        self.assertEquals(0, len(parser._parsing_warnings))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = TypePlain()
        returned = parser.parse("`created` date")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertEquals('created', parser._name)
