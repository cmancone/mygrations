import unittest

from mygrations.formats.mysql.file_reader.parsers.insert_values import InsertValues
class TestInsertValues(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = InsertValues()
        returned = parser.parse("(      'name', 'bob', 'okay', 1),")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEqual('', returned)

        # all we really have is the list of values
        self.assertEqual(['name', 'bob', 'okay', '1'], parser.values)
        self.assertTrue(parser.has_comma)

    def test_optional_comma(self):

        # parse typical insert values
        parser = InsertValues()
        returned = parser.parse("('name', 'bob', 'okay', 1)")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEqual('', returned)

        # all we really have is the list of values
        self.assertEqual(['name', 'bob', 'okay', '1'], parser.values)
        self.assertFalse(parser.has_comma)

    def test_return(self):

        # parse typical insert values
        parser = InsertValues()
        returned = parser.parse("('name','bob','okay',1), ('name','bob')")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEqual("('name','bob')", returned)

        # all we really have is the list of values
        self.assertEqual(['name', 'bob', 'okay', '1'], parser.values)
        self.assertTrue(parser.has_comma)
