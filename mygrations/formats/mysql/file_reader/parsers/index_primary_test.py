import unittest

from mygrations.formats.mysql.file_reader.parsers.index_primary import IndexPrimary
class TestIndexPrimary(unittest.TestCase):
    def test_simple(self):

        # parse a typical KEY
        parser = IndexPrimary()
        returned = parser.parse('PRIMARY KEY (`id`),')

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals('', returned)

        # we should have lots of data now
        self.assertEquals(['id'], parser.columns)
        self.assertEquals(parser.index_type, 'PRIMARY')
        self.assertTrue(parser.has_comma)
        self.assertEquals('PRIMARY KEY (`id`)', str(parser))

    def test_optional_comma(self):

        # ending comma is optional
        parser = IndexPrimary()
        returned = parser.parse('PRIMARY KEY (`id`)')

        # we should have matched
        self.assertEquals(['id'], parser.columns)
        self.assertTrue(parser.matched)
        self.assertFalse(parser.has_comma)
        self.assertEquals('PRIMARY KEY (`id`)', str(parser))

    def test_optional_quotes(self):

        # key name quotes are optional
        parser = IndexPrimary()
        returned = parser.parse('PRIMARY KEY (sup)')

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertEquals(['sup'], parser.columns)
        self.assertEquals('PRIMARY KEY (`sup`)', str(parser))
