import unittest

from mygrations.formats.mysql.file_reader.parsers.type_text import TypeText


class TestTypeText(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypeText()
        returned = parser.parse("name text not null,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)

        self.assertEqual("name", parser._name)
        self.assertEqual("text", parser._column_type)
        self.assertFalse(parser._null)
        self.assertTrue(parser.has_comma)
        self.assertIsNone(parser._character_set)
        self.assertIsNone(parser._collate)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_character_set(self):

        # parse typical insert values
        parser = TypeText()
        returned = parser.parse("name text character set 'blah' collate 'boo',")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)

        self.assertEqual("name", parser._name)
        self.assertEqual("text", parser._column_type)
        self.assertTrue(parser._null)
        self.assertTrue(parser.has_comma)
        self.assertEqual("blah", parser._character_set)
        self.assertEqual("boo", parser._collate)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = TypeText()
        returned = parser.parse("`name` text not null")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("name", parser._name)
