import unittest

from mygrations.formats.mysql.file_reader.parsers.type_numeric import TypeNumeric


class TestTypeNumeric(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypeNumeric()
        returned = parser.parse("created int(10) not null default 0,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)

        self.assertEqual("created", parser._name)
        self.assertEqual("int", parser._column_type)
        self.assertEqual("10", parser._length)
        self.assertFalse(parser._unsigned)
        self.assertFalse(parser._null)
        self.assertFalse(parser._auto_increment)
        self.assertEqual("0", parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_auto_increment(self):

        # parse typical insert values
        parser = TypeNumeric()
        returned = parser.parse("created int(10) not null auto_increment,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)

        self.assertEqual("created", parser._name)
        self.assertEqual("int", parser._column_type)
        self.assertEqual("10", parser._length)
        self.assertTrue(parser._auto_increment)
        self.assertFalse(parser._unsigned)
        self.assertFalse(parser._null)
        self.assertEqual(None, parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_optional_default(self):

        # parse typical insert values
        parser = TypeNumeric()
        returned = parser.parse("created int(10) UNSIGNED")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)

        self.assertEqual("created", parser._name)
        self.assertEqual("int", parser._column_type)
        self.assertTrue(parser._unsigned)
        self.assertEqual("10", parser._length)
        self.assertTrue(parser._null)
        self.assertEqual(None, parser._default)
        self.assertFalse(parser.has_comma)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = TypeNumeric()
        returned = parser.parse("`created` int(10) UNSIGNED")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("created", parser._name)

    def test_integer_normalized_to_int(self):
        parser = TypeNumeric()
        returned = parser.parse("count integer(10) NOT NULL DEFAULT 0,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("count", parser._name)
        self.assertEqual("int", parser._column_type)
        self.assertEqual("10", parser._length)

    def test_integer_uppercase_normalized_to_int(self):
        parser = TypeNumeric()
        returned = parser.parse("count INTEGER(1),")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("int", parser._column_type)
        self.assertEqual("1", parser._length)
