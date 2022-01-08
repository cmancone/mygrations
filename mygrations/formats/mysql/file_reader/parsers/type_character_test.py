import unittest

from mygrations.formats.mysql.file_reader.parsers.type_character import TypeCharacter
class TestTypeCharacter(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypeCharacter()
        returned = parser.parse("name varchar(255) not null default 'sup',")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('name', parser._name)
        self.assertEquals('varchar', parser._column_type)
        self.assertEquals('255', parser._length)
        self.assertFalse(parser._null)
        self.assertEquals('sup', parser._default)
        self.assertTrue(parser.has_comma)
        self.assertTrue(parser._character_set is None)
        self.assertTrue(parser._collate is None)

    def test_character_set(self):

        # parse typical insert values
        parser = TypeCharacter()
        returned = parser.parse("name varchar(255) not null default 'sup' character set 'blah' collate 'boo',")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('name', parser._name)
        self.assertEquals('varchar', parser._column_type)
        self.assertEquals('255', parser._length)
        self.assertFalse(parser._null)
        self.assertEquals('sup', parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEquals('blah', parser._character_set)
        self.assertEquals('boo', parser._collate)

    def test_optional_default(self):

        # parse typical insert values
        parser = TypeCharacter()
        returned = parser.parse("name varchar(255)")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('name', parser._name)
        self.assertEquals('varchar', parser._column_type)
        self.assertEquals('255', parser._length)
        self.assertTrue(parser._null)
        self.assertEquals(None, parser._default)
        self.assertFalse(parser.has_comma)
        self.assertTrue(parser._character_set is None)
        self.assertTrue(parser._collate is None)

    def test_empty_default(self):

        # parse typical insert values
        parser = TypeCharacter()
        returned = parser.parse("name varchar(255) default ''")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('', parser._default)

    def test_strip_backticks(self):

        # parse typical insert values
        parser = TypeCharacter()
        returned = parser.parse("`name` varchar(255)")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('name', parser._name)
