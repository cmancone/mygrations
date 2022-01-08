import unittest

from mygrations.formats.mysql.file_reader.insert_parser import InsertParser
class test_insert_parser(unittest.TestCase):
    def test_simple(self):

        parser = InsertParser()
        returned = parser.parse("INSERT INTO test_table (`col1`,`col2`) VALUES ('val','val2');")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have matched everything
        self.assertEquals('', returned)

        # we should have lots of data now
        self.assertEquals('test_table', parser.table)
        self.assertEquals(['col1', 'col2'], parser.columns)
        self.assertEquals([['val', 'val2']], parser.raw_rows)
        self.assertTrue(parser.has_semicolon)
        self.assertEquals([], parser.parsing_errors)

    def test_multiple_values(self):

        parser = InsertParser()
        returned = parser.parse("INSERT INTO test_table (`col1`,`col2`) VALUES ('val','val2'),('val3','val4')")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have matched everything
        self.assertEquals('', returned)

        # we should have lots of data now
        self.assertEquals('test_table', parser.table)
        self.assertEquals(['col1', 'col2'], parser.columns)
        self.assertEquals([['val', 'val2'], ['val3', 'val4']], parser.raw_rows)
        self.assertFalse(parser.has_semicolon)
        self.assertEquals([], parser.parsing_errors)

    def test_missing_comma(self):

        parser = InsertParser()
        returned = parser.parse("INSERT INTO test_table (`col1`,`col2`) VALUES ('val','val2')('val3','val4')")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have matched everything
        self.assertEquals('', returned)

        # we should have lots of data now
        self.assertEquals('test_table', parser.table)
        self.assertEquals(['col1', 'col2'], parser.columns)
        self.assertEquals([['val', 'val2'], ['val3', 'val4']], parser.raw_rows)
        self.assertFalse(parser.has_semicolon)
        self.assertEquals(1, len(parser.parsing_warnings))
