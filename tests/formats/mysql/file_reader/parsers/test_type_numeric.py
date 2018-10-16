import unittest

from mygrations.formats.mysql.file_reader.parsers.type_numeric import type_numeric
class test_type_numeric(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = type_numeric()
        returned = parser.parse("created int(10) not null default 0,")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('created', parser.name)
        self.assertEquals('INT', parser.column_type)
        self.assertEquals('10', parser.length)
        self.assertFalse(parser.unsigned)
        self.assertFalse(parser.null)
        self.assertFalse(parser.auto_increment)
        self.assertEquals('0', parser.default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertEquals("`created` INT(10) NOT NULL DEFAULT 0", str(parser))

    def test_auto_increment(self):

        # parse typical insert values
        parser = type_numeric()
        returned = parser.parse("created int(10) not null auto_increment,")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('created', parser.name)
        self.assertEquals('INT', parser.column_type)
        self.assertEquals('10', parser.length)
        self.assertTrue(parser.auto_increment)
        self.assertFalse(parser.unsigned)
        self.assertFalse(parser.null)
        self.assertEquals(None, parser.default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertEquals("`created` INT(10) NOT NULL AUTO_INCREMENT", str(parser))

    def test_optional_default(self):

        # parse typical insert values
        parser = type_numeric()
        returned = parser.parse("created int(10) UNSIGNED")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('created', parser.name)
        self.assertEquals('INT', parser.column_type)
        self.assertTrue(parser.unsigned)
        self.assertEquals('10', parser.length)
        self.assertTrue(parser.null)
        self.assertEquals(None, parser.default)
        self.assertFalse(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertEquals("`created` INT(10) UNSIGNED", str(parser))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = type_numeric()
        returned = parser.parse("`created` int(10) UNSIGNED")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertEquals('created', parser.name)
        self.assertEquals("`created` INT(10) UNSIGNED", str(parser))

    def test_warning_for_string_default(self):

        # parse typical insert values
        parser = type_numeric()
        returned = parser.parse("created int(10) default '0'")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('does not need to be quoted' in parser.warnings[0])
        self.assertEquals("`created` INT(10) DEFAULT 0", str(parser))

    def test_not_null_needs_default(self):

        # parse typical insert values
        parser = type_numeric()
        returned = parser.parse("name int(10) NOT NULL")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('is not null and has no default' in parser.warnings[0])

    def test_char_field_defaults_should_be_quoted(self):

        parser = type_numeric()
        returned = parser.parse("name varchar(255) DEFAULT asdf")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('should be quoted' in parser.warnings[0])

    def test_char_fields_should_not_be_unsigned(self):

        parser = type_numeric()
        returned = parser.parse("name varchar(255) UNSIGNED NOT NULL DEFAULT 'asdf'")

        self.assertTrue(parser.is_char)
        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('character type and cannot be unsigned' in parser.errors[0])

    def test_char_fields_should_not_auto_increment(self):

        parser = type_numeric()
        returned = parser.parse("name varchar(255) NOT NULL AUTO_INCREMENT")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('only numeric fields can auto increment' in parser.errors[0])

    def test_autoincrement_can_be_not_null_and_no_default(self):

        parser = type_numeric()
        returned = parser.parse("name int(10) UNSIGNED NOT NULL AUTO_INCREMENT")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertEquals(0, len(parser.warnings))

    def test_number_field_defaults_should_not_be_quoted(self):

        parser = type_numeric()
        returned = parser.parse("name int(10) DEFAULT '0'")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('does not need to be quoted' in parser.warnings[0])

    # not for everyone
    def test_disallowed_types(self):

        # anything not on the whitelist (this is not a complete list)
        for coltype in ['date', 'bob', 'difjerejrie']:
            parser = type_numeric()
            returned = parser.parse("name %s(10)" % coltype)
            self.assertTrue(
                'not allowed to have a length' in parser.errors[0],
                'Type %s should not be allowed to be numeric but is' % coltype
            )

    # everything on the white list is allowed to be numeric
    def test_valid_column_type(self):

        for coltype in [
            'bit', 'tinyint', 'smallint', 'mediumint', 'int', 'integer', 'bigint', 'decimal', 'numeric', 'char',
            'varchar'
        ]:

            parser = type_numeric()
            returned = parser.parse('name %s(10)' % coltype)

            self.assertTrue(parser.matched)
            self.assertEquals('', returned)
            self.assertEquals(0, len(parser.errors), 'Type %s should not be allowed to have decimals but is' % coltype)
