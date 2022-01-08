import unittest

from mygrations.formats.mysql.file_reader.parsers.index_key import IndexKey
class TestIndexKey(unittest.TestCase):
    def test_simple(self):

        # parse a typical KEY
        parser = IndexKey()
        returned = parser.parse('KEY `users_email` (`email`),')

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals('', returned)

        # we should have lots of data now
        self.assertEquals('users_email', parser.name)
        self.assertEquals(['email'], parser.columns)
        self.assertTrue(parser.has_comma)
        self.assertEquals('KEY `users_email` (`email`)', str(parser))

    def test_optional_comma(self):

        # ending comma is optional
        parser = IndexKey()
        returned = parser.parse('KEY `users_email` (`email`)')

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertFalse(parser.has_comma)
        self.assertEquals('KEY `users_email` (`email`)', str(parser))

    def test_optional_quotes(self):

        # key name quotes are optional
        parser = IndexKey()
        returned = parser.parse('KEY users_email (`email`)')

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertEquals('users_email', parser.name)
        self.assertEquals('KEY `users_email` (`email`)', str(parser))

    def test_multiple_columns(self):

        # multi column index
        parser = IndexKey()
        returned = parser.parse('KEY `users_email` (`email`,`username`,`password`),')

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals('', returned)

        # we should have lots of data now
        self.assertEquals('users_email', parser.name)
        self.assertEquals(['email', 'username', 'password'], parser.columns)
        self.assertTrue(parser.has_comma)
        self.assertEquals('KEY `users_email` (`email`,`username`,`password`)', str(parser))
