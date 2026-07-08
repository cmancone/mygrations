import unittest

from mygrations.formats.mysql.file_reader.parsers.type_plain import TypePlain


class TestTypePlain(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = TypePlain()
        returned = parser.parse("created date NOT NULL DEFAULT 'bob',")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)

        self.assertEqual("created", parser._name)
        self.assertEqual("date", parser._column_type)
        self.assertFalse(parser._null)
        self.assertEqual("bob", parser._default)
        self.assertTrue(parser.has_comma)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_optional_default(self):

        # parse typical insert values
        parser = TypePlain()
        returned = parser.parse("created date")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)

        self.assertEqual("created", parser._name)
        self.assertEqual("date", parser._column_type)
        self.assertTrue(parser._null)
        self.assertEqual(None, parser._default)
        self.assertFalse(parser.has_comma)
        self.assertEqual(0, len(parser._parsing_errors))
        self.assertEqual(0, len(parser._parsing_warnings))

    def test_primary_key_before_default(self):
        parser = TypePlain()
        returned = parser.parse("id INT UNSIGNED NOT NULL PRIMARY KEY DEFAULT 0,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("id", parser._name)
        self.assertEqual("INT", parser._column_type)
        self.assertTrue(parser._unsigned)
        self.assertFalse(parser._null)
        self.assertTrue(parser._is_primary_key)
        self.assertEqual("0", parser._default)
        self.assertTrue(parser.has_comma)

    def test_primary_key_after_default(self):
        parser = TypePlain()
        returned = parser.parse("id INT UNSIGNED NOT NULL DEFAULT 0 PRIMARY KEY,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("id", parser._name)
        self.assertEqual("INT", parser._column_type)
        self.assertTrue(parser._unsigned)
        self.assertFalse(parser._null)
        self.assertTrue(parser._is_primary_key)
        self.assertEqual("0", parser._default)
        self.assertTrue(parser.has_comma)

    def test_boolean_type(self):
        parser = TypePlain()
        returned = parser.parse("is_active BOOLEAN,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("is_active", parser._name)
        self.assertEqual("TINYINT", parser._column_type)
        self.assertEqual("1", parser._length)
        self.assertTrue(parser.has_comma)

    def test_boolean_with_default_true(self):
        parser = TypePlain()
        returned = parser.parse("is_active BOOLEAN DEFAULT TRUE,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("TINYINT", parser._column_type)
        self.assertEqual("1", parser._length)
        self.assertEqual("1", parser._default)

    def test_boolean_with_default_false(self):
        parser = TypePlain()
        returned = parser.parse("is_active BOOLEAN DEFAULT FALSE,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("TINYINT", parser._column_type)
        self.assertEqual("1", parser._length)
        self.assertEqual("0", parser._default)

    def test_primary_key_implies_not_null(self):
        parser = TypePlain()
        returned = parser.parse("id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("id", parser._name)
        self.assertEqual("INT", parser._column_type)
        self.assertTrue(parser._unsigned)
        self.assertFalse(parser._null)
        self.assertTrue(parser._is_primary_key)
        self.assertTrue(parser._auto_increment)

    def test_primary_key_without_not_null_without_auto_increment(self):
        parser = TypePlain()
        returned = parser.parse("id INT UNSIGNED PRIMARY KEY,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertFalse(parser._null)
        self.assertTrue(parser._is_primary_key)
        self.assertFalse(parser._auto_increment)

    def test_strip_backticks(self):

        # parse typical insert values
        parser = TypePlain()
        returned = parser.parse("`created` date")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("created", parser._name)

    def test_integer_normalized_to_int(self):
        parser = TypePlain()
        returned = parser.parse("access_level INTEGER,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("access_level", parser._name)
        self.assertEqual("int", parser._column_type)

    def test_integer_with_default_normalized_to_int(self):
        parser = TypePlain()
        returned = parser.parse("gitlab_access_level INTEGER NOT NULL DEFAULT 0,")

        self.assertTrue(parser.matched)
        self.assertEqual("", returned)
        self.assertEqual("int", parser._column_type)
        self.assertFalse(parser._null)
        self.assertEqual("0", parser._default)
