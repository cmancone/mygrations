import unittest

from mygrations.formats.mysql.file_reader.parsers.type_datetime import TypeDateTime
class TestTypeDateTime(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypeDateTime()
        returned = parser.parse("name datetime not null default 'YY-MM-DD HH-MM-SS',")

        self.assertTrue(parser.matched)
        self.assertEqual('', returned)

        self.assertEqual('name', parser._name)
        self.assertEqual('datetime', parser._column_type)
        self.assertFalse(parser._null)
        self.assertEqual('YY-MM-DD HH-MM-SS', parser._default)
        self.assertTrue(parser.has_comma)
        self.assertTrue(parser._character_set is None)
        self.assertTrue(parser._collate is None)
