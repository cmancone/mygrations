import unittest

from mygrations.formats.mysql.file_reader.parsers.index_unique import index_unique
class test_index_unique(unittest.TestCase):
    def test_simple(self):

        # parse a typical UNIQUE KEY
        parser = index_unique()
        returned = parser.parse('UNIQUE KEY `users_email` (`email`),')

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals('', returned)

        # we should have lots of data now
        self.assertEquals('users_email', parser.name)
        self.assertEquals(['email'], parser.columns)
        self.assertEquals(parser.index_type, 'UNIQUE')
        self.assertTrue(parser.has_comma)
        self.assertEquals('UNIQUE KEY `users_email` (`email`)', str(parser))

    def test_optional_comma(self):

        # ending comma is optional
        parser = index_unique()
        returned = parser.parse('UNIQUE KEY `users_email` (`email`)')

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertFalse(parser.has_comma)
        self.assertEquals('UNIQUE KEY `users_email` (`email`)', str(parser))

    def test_optional_quotes(self):

        # key name quotes are optional
        parser = index_unique()
        returned = parser.parse('UNIQUE KEY users_email (`email`)')

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertEquals('users_email', parser.name)
        self.assertEquals('UNIQUE KEY `users_email` (`email`)', str(parser))

    def test_multiple_columns(self):

        # multi column index
        parser = index_unique()
        returned = parser.parse('UNIQUE KEY `users_email` (`email`,`username`,`password`),')

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals('', returned)

        # we should have lots of data now
        self.assertEquals('users_email', parser.name)
        self.assertEquals(['email', 'username', 'password'], parser.columns)
        self.assertEquals(parser.index_type, 'UNIQUE')
        self.assertTrue(parser.has_comma)
        self.assertEquals('UNIQUE KEY `users_email` (`email`,`username`,`password`)', str(parser))
