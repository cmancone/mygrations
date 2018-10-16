import unittest

from mygrations.formats.mysql.file_reader.parsers.type_plain import type_plain
class test_type_plain(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = type_plain()
        returned = parser.parse("created date NOT NULL DEFAULT 'bob',")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('created', parser.name)
        self.assertEquals('DATE', parser.column_type)
        self.assertFalse(parser.null)
        self.assertEquals('bob', parser.default)
        self.assertTrue(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertEquals("`created` DATE NOT NULL DEFAULT 'bob'", str(parser))

    def test_optional_default(self):

        # parse typical insert values
        parser = type_plain()
        returned = parser.parse("created date")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)

        self.assertEquals('column', parser.definition_type)
        self.assertEquals('created', parser.name)
        self.assertEquals('DATE', parser.column_type)
        self.assertTrue(parser.null)
        self.assertEquals(None, parser.default)
        self.assertFalse(parser.has_comma)
        self.assertEquals(0, len(parser.errors))
        self.assertEquals(0, len(parser.warnings))
        self.assertEquals("`created` DATE", str(parser))

    def test_strip_backticks(self):

        # parse typical insert values
        parser = type_plain()
        returned = parser.parse("`created` date")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertEquals('column', parser.definition_type)
        self.assertEquals('created', parser.name)
        self.assertEquals("`created` DATE", str(parser))

    def test_not_null_needs_default(self):

        # parse typical insert values
        parser = type_plain()
        returned = parser.parse("created date NOT NULL")

        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('is not null and has no default' in parser.warnings[0])
