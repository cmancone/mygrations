import unittest

from mygrations.formats.mysql.file_reader.parsers.type_numeric import TypeNumeric
class TestTypeNumeric(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypeNumeric()
        returned = parser.parse("created int(10) not null default 0,")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('created', parser._name)
        self.assertEquals('int', parser._column_type)
        self.assertEquals('10', parser._length)
        self.assertFalse(parser._unsigned)
        self.assertFalse(parser._null)
        self.assertFalse(parser._auto_increment)
        self.assertEquals('0', parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser._parsing_errors))
        self.assertEquals(0, len(parser._parsing_warnings))

    def test_auto_increment(self):

        # parse typical insert values
        parser = TypeNumeric()
        returned = parser.parse("created int(10) not null auto_increment,")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('created', parser._name)
        self.assertEquals('int', parser._column_type)
        self.assertEquals('10', parser._length)
        self.assertTrue(parser._auto_increment)
        self.assertFalse(parser._unsigned)
        self.assertFalse(parser._null)
        self.assertEquals(None, parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser._parsing_errors))
        self.assertEquals(0, len(parser._parsing_warnings))

    def test_optional_default(self):

        # parse typical insert values
        parser = TypeNumeric()
        returned = parser.parse("created int(10) UNSIGNED")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('created', parser._name)
        self.assertEquals('int', parser._column_type)
        self.assertTrue(parser._unsigned)
        self.assertEquals('10', parser._length)
        self.assertTrue(parser._null)
        self.assertEquals(None, parser._default)
        self.assertFalse(parser.has_comma)
        self.assertEquals(0, len(parser._parsing_errors))
        self.assertEquals(0, len(parser._parsing_warnings))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = TypeNumeric()
        returned = parser.parse("`created` int(10) UNSIGNED")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertEquals('created', parser._name)
