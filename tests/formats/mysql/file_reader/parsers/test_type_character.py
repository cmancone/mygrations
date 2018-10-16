import unittest

from mygrations.formats.mysql.file_reader.parsers.type_character import type_character
class test_type_character(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = type_character()
        returned = parser.parse("name varchar(255) not null default 'sup',")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('name', parser.name)
        self.assertEquals('VARCHAR', parser.column_type)
        self.assertEquals('255', parser.length)
        self.assertFalse(parser.null)
        self.assertEquals('sup', parser.default)
        self.assertTrue(parser.has_comma)
        self.assertTrue(parser.character_set is None)
        self.assertTrue(parser.collate is None)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals("`name` VARCHAR(255) NOT NULL DEFAULT 'sup'", str(parser))

    def test_character_set(self):

        # parse typical insert values
        parser = type_character()
        returned = parser.parse("name varchar(255) not null default 'sup' character set 'blah' collate 'boo',")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('name', parser.name)
        self.assertEquals('VARCHAR', parser.column_type)
        self.assertEquals('255', parser.length)
        self.assertFalse(parser.null)
        self.assertEquals('sup', parser.default)
        self.assertTrue(parser.has_comma)
        self.assertEquals('BLAH', parser.character_set)
        self.assertEquals('BOO', parser.collate)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals("`name` VARCHAR(255) NOT NULL DEFAULT 'sup' CHARACTER SET 'BLAH' COLLATE 'BOO'", str(parser))

    def test_optional_default(self):

        # parse typical insert values
        parser = type_character()
        returned = parser.parse("name varchar(255)")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('name', parser.name)
        self.assertEquals('VARCHAR', parser.column_type)
        self.assertEquals('255', parser.length)
        self.assertTrue(parser.null)
        self.assertEquals(None, parser.default)
        self.assertFalse(parser.has_comma)
        self.assertTrue(parser.character_set is None)
        self.assertTrue(parser.collate is None)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals("`name` VARCHAR(255)", str(parser))

    def test_empty_default(self):

        # parse typical insert values
        parser = type_character()
        returned = parser.parse("name varchar(255) default ''")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('', parser.default)
        self.assertEquals("`name` VARCHAR(255) DEFAULT ''", str(parser))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = type_character()
        returned = parser.parse("`name` varchar(255)")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('name', parser.name)
        self.assertEquals("`name` VARCHAR(255)", str(parser))

    def test_not_null_needs_default(self):

        # parse typical insert values
        parser = type_character()
        returned = parser.parse("name varchar(255) NOT NULL")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertTrue('is not null and has no default' in parser.warnings[0])

    # only char and varchar can have collate
    def test_disallowed_collate(self):

        # parse typical insert values
        parser = type_character()
        returned = parser.parse("name int(10) collate 'blah'")
        self.assertTrue('is not allowed to have a collation or character set' in parser.errors[0])

    def test_disallowed_character_set(self):

        # parse typical insert values
        parser = type_character()
        returned = parser.parse("name int(10) character set 'blah'")
        self.assertTrue('is not allowed to have a collation or character set' in parser.errors[0])

    # some types are not allowed to have a length
    def test_invalid_column_type(self):

        for coltype in [
            'date', 'year', 'tinyblob', 'blob', 'mediumblob', 'longblob', 'tinytext', 'text', 'mediumtext', 'longtext',
            'json'
        ]:

            parser = type_character()
            returned = parser.parse('name %s(10)' % coltype)

            self.assertTrue(parser.matched)
            self.assertEquals('', returned)
            self.assertTrue('not allowed to have a length' in parser.errors[0])
