import unittest

from mygrations.formats.mysql.file_reader.parsers.type_decimal import TypeDecimal
class TestTypeDecimal(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypeDecimal()
        returned = parser.parse("latitude float(10,7) not null default 0,")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('latitude', parser._name)
        self.assertEquals('float', parser._column_type)
        self.assertEquals('10,7', parser._length)
        self.assertFalse(parser._unsigned)
        self.assertFalse(parser._null)
        self.assertEquals('0', parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser._parsing_errors))
        self.assertEquals(0, len(parser._parsing_warnings))

    def test_optional_default(self):

        # parse typical insert values
        parser = TypeDecimal()
        returned = parser.parse("latitude float(10,7) UNSIGNED")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('latitude', parser._name)
        self.assertEquals('float', parser._column_type)
        self.assertTrue(parser._unsigned)
        self.assertEquals('10,7', parser._length)
        self.assertTrue(parser._null)
        self.assertEquals(None, parser._default)
        self.assertFalse(parser.has_comma)
        self.assertEquals(0, len(parser._parsing_errors))
        self.assertEquals(0, len(parser._parsing_warnings))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = TypeDecimal()
        returned = parser.parse("`latitude` float(10,7)")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('latitude', parser._name)

    def test_warning_for_string_default(self):

        # parse typical insert values
        parser = TypeDecimal()
        returned = parser.parse("latitude float(10,7) default '0'")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('has a numeric type but its default value is a string' in parser._parsing_warnings[0])
