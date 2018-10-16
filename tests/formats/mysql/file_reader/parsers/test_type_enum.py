import unittest

from mygrations.formats.mysql.file_reader.parsers.type_enum import type_enum
class test_type_enum(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = type_enum()
        returned = parser.parse("options enum('bob','joe','ray') not null default 'bob',")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('options', parser.name)
        self.assertEquals('ENUM', parser.column_type)
        self.assertEquals(['bob', 'joe', 'ray'], parser.values)
        self.assertFalse(parser.null)
        self.assertEquals('bob', parser.default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertEquals("`options` ENUM('bob','joe','ray') NOT NULL DEFAULT 'bob'", str(parser))

    def test_optional_default(self):

        # parse typical insert values
        parser = type_enum()
        returned = parser.parse("options enum('bob','joe','ray')")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('options', parser.name)
        self.assertEquals('ENUM', parser.column_type)
        self.assertEquals(['bob', 'joe', 'ray'], parser.values)
        self.assertTrue(parser.null)
        self.assertEquals(None, parser.default)
        self.assertFalse(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertEquals("`options` ENUM('bob','joe','ray')", str(parser))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = type_enum()
        returned = parser.parse("`options` enum('bob','joe','ray')")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertEquals('options', parser.name)

    def test_warning_for_no_quote_default(self):

        # parse typical insert values
        parser = type_enum()
        returned = parser.parse("options enum('bob','joe','ray') default bob")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('should have quotes' in parser.warnings[0])
        self.assertEquals("`options` ENUM('bob','joe','ray') DEFAULT 'bob'", str(parser))

    def test_error_for_invalid_default(self):

        # parse typical insert values
        parser = type_enum()
        returned = parser.parse("options enum('bob','joe','ray') default asdf")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('this is not an allowed value' in parser.errors[0])

    def test_not_null_needs_default(self):

        # parse typical insert values
        parser = type_enum()
        returned = parser.parse("options enum('bob','joe','ray') not null")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertTrue('is not null and has no default' in parser.warnings[0])

    # only some can match this type
    def test_allowed_types(self):

        # parse typical insert values
        for coltype in ['set', 'enum']:
            parser = type_enum()
            returned = parser.parse("name %s('bob','joe','ray')" % coltype)
            self.assertEquals(
                0, len(parser.errors), 'Type %s should be allowed to use set/enum values but is not' % coltype
            )

    # everything else is not allowed to have a length
    def test_invalid_column_type(self):

        for coltype in [
            'date', 'year', 'tinyblob', 'blob', 'mediumblob', 'longblob', 'tinytext', 'text', 'mediumtext', 'longtext',
            'json', 'char', 'varchar', 'biejfiejrei'
        ]:

            parser = type_enum()
            returned = parser.parse("name %s('bob','joe','ray')" % coltype)

            self.assertTrue(parser.matched)
            self.assertEquals('', returned)
            self.assertTrue(
                'not allowed to have a list of values' in parser.errors[0],
                'Type %s should not be allowed to use set/enum but is' % coltype
            )
