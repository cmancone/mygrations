import unittest

from mygrations.formats.mysql.file_reader.parsers.type_decimal import type_decimal
class test_type_decimal(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = type_decimal()
        returned = parser.parse("latitude float(10,7) not null default 0,")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('latitude', parser.name)
        self.assertEquals('FLOAT', parser.column_type)
        self.assertEquals('10,7', parser.length)
        self.assertFalse(parser.unsigned)
        self.assertFalse(parser.null)
        self.assertEquals('0', parser.default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertTrue(parser.character_set is None)
        self.assertTrue(parser.collate is None)
        self.assertEquals("`latitude` FLOAT(10,7) NOT NULL DEFAULT 0", str(parser))

    def test_optional_default(self):

        # parse typical insert values
        parser = type_decimal()
        returned = parser.parse("latitude float(10,7) UNSIGNED")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('latitude', parser.name)
        self.assertEquals('FLOAT', parser.column_type)
        self.assertTrue(parser.unsigned)
        self.assertEquals('10,7', parser.length)
        self.assertTrue(parser.null)
        self.assertEquals(None, parser.default)
        self.assertFalse(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertEquals("`latitude` FLOAT(10,7) UNSIGNED", str(parser))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = type_decimal()
        returned = parser.parse("`latitude` float(10,7)")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('latitude', parser.name)
        self.assertEquals("`latitude` FLOAT(10,7)", str(parser))

    def test_warning_for_string_default(self):

        # parse typical insert values
        parser = type_decimal()
        returned = parser.parse("latitude float(10,7) default '0'")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('does not need to be quoted' in parser.warnings[0])

    def test_not_null_needs_default(self):

        # parse typical insert values
        parser = type_decimal()
        returned = parser.parse("name float(10,7) NOT NULL")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertTrue('is not null and has no default' in parser.warnings[0])

    # only some can have decimals
    def test_disallowed_collate(self):

        # parse typical insert values
        for coltype in ['real', 'double', 'float', 'decimal', 'numeric']:
            parser = type_decimal()
            returned = parser.parse("name %s(10,7)" % coltype)
            self.assertEquals(0, len(parser.errors), 'Type %s should be allowed to have decimals but is not' % coltype)

    # everything else is not allowed to have a length
    def test_invalid_column_type(self):

        for coltype in [
            'date', 'year', 'tinyblob', 'blob', 'mediumblob', 'longblob', 'tinytext', 'text', 'mediumtext', 'longtext',
            'json', 'char', 'varchar', 'biejfiejrei'
        ]:

            parser = type_decimal()
            returned = parser.parse('name %s(10,7)' % coltype)

            self.assertTrue(parser.matched)
            self.assertEquals('', returned)
            self.assertTrue(
                'not allowed to have a decimal length' in parser.errors[0],
                'Type %s should not be allowed to have decimals but is' % coltype
            )
