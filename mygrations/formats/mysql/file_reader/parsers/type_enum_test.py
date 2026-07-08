import unittest

from mygrations.formats.mysql.file_reader.parsers.type_enum import TypeEnum
class TestTypeEnum(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypeEnum()
        returned = parser.parse("options enum('bob','joe','ray') not null default 'bob',")

        self.assertTrue(parser.matched)
        self.assertEqual('', returned)

        self.assertEqual('options', parser._name)
        self.assertEqual('enum', parser._column_type)
        self.assertEqual(['bob', 'joe', 'ray'], parser._enum_values)
        self.assertFalse(parser._null)
        self.assertEqual('bob', parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_optional_default(self):

        # parse typical insert values
        parser = TypeEnum()
        returned = parser.parse("options enum('bob','joe','ray')")

        self.assertTrue(parser.matched)
        self.assertEqual('', returned)

        self.assertEqual('options', parser._name)
        self.assertEqual('enum', parser._column_type)
        self.assertEqual(['bob', 'joe', 'ray'], parser._enum_values)
        self.assertTrue(parser._null)
        self.assertEqual(None, parser._default)
        self.assertFalse(parser.has_comma)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = TypeEnum()
        returned = parser.parse("`options` enum('bob','joe','ray')")

        self.assertTrue(parser.matched)
        self.assertEqual('', returned)
        self.assertEqual('options', parser._name)

    def test_warning_for_no_quote_default(self):

        # parse typical insert values
        parser = TypeEnum()
        returned = parser.parse("options enum('bob','joe','ray') default bob")

        self.assertTrue(parser.matched)
        self.assertEqual('', returned)
        self.assertTrue('should have quotes' in parser._parsing_warnings[0])
