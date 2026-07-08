import unittest

from mygrations.formats.mysql.file_reader.parsers.index_unique import IndexUnique
class TestIndexUnique(unittest.TestCase):
    def test_simple(self):

        # parse a typical UNIQUE KEY
        parser = IndexUnique()
        returned = parser.parse('UNIQUE KEY `users_email` (`email`),')

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEqual('', returned)

        # we should have lots of data now
        self.assertEqual('users_email', parser.name)
        self.assertEqual(['email'], parser.columns)
        self.assertEqual(parser.index_type, 'UNIQUE')
        self.assertTrue(parser.has_comma)
        self.assertEqual('UNIQUE KEY `users_email` (`email`)', str(parser))

    def test_optional_comma(self):

        # ending comma is optional
        parser = IndexUnique()
        returned = parser.parse('UNIQUE KEY `users_email` (`email`)')

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertFalse(parser.has_comma)
        self.assertEqual('UNIQUE KEY `users_email` (`email`)', str(parser))

    def test_optional_quotes(self):

        # key name quotes are optional
        parser = IndexUnique()
        returned = parser.parse('UNIQUE KEY users_email (`email`)')

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertEqual('users_email', parser.name)
        self.assertEqual('UNIQUE KEY `users_email` (`email`)', str(parser))

    def test_multiple_columns(self):

        # multi column index
        parser = IndexUnique()
        returned = parser.parse('UNIQUE KEY `users_email` (`email`,`username`,`password`),')

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEqual('', returned)

        # we should have lots of data now
        self.assertEqual('users_email', parser.name)
        self.assertEqual(['email', 'username', 'password'], parser.columns)
        self.assertEqual(parser.index_type, 'UNIQUE')
        self.assertTrue(parser.has_comma)
        self.assertEqual('UNIQUE KEY `users_email` (`email`,`username`,`password`)', str(parser))
