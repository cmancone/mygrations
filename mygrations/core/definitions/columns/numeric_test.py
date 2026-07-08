import unittest
from .numeric import Numeric


class NumericTest(unittest.TestCase):
    def test_is_the_same(self):
        attrs = {"length": "5,2", "default": "0.00"}

        column1 = Numeric("test", "DECIMAL", **attrs)
        column2 = Numeric("test", "DECIMAL", **attrs)
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        column1 = Numeric("test", "DECIMAL", **attrs)
        column2 = Numeric("test", "DECIMAL", **{**attrs, "default": "0.02"})
        self.assertFalse(column1.is_really_the_same_as(column2))
        self.assertFalse(column2.is_really_the_same_as(column1))

        column1 = Numeric("test", "DECIMAL", **attrs)
        column2 = Numeric("test", "DECIMAL", **{**attrs, "default": "0.001"})
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        column1 = Numeric("test", "DECIMAL", **attrs)
        column2 = Numeric("test", "DECIMAL", **{**attrs, "default": 0})
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

    def test_default_errors(self):
        self.assertEqual(
            [f"Column 'test' of type 'DECIMAL' cannot have a string value as a default"],
            Numeric("test", "DECIMAL", default="").schema_errors,
        )
        self.assertEqual(
            [f"Column 'test' of type 'INT' must have an integer value as a default"],
            Numeric("test", "INT", default=5.0).schema_errors,
        )
        self.assertEqual(
            [f"Column 'test' of type 'BIT' must have a default of 1 or 0"],
            Numeric("test", "BIT", default=5).schema_errors,
        )
        self.assertEqual([], Numeric("test", "BIT", default=1).schema_errors)
        self.assertEqual([], Numeric("test", "INT", default=5).schema_errors)
        self.assertEqual([], Numeric("test", "FLOAT", default=5.0).schema_errors)

    def test_length_errors(self):
        self.assertEqual(
            [f"Column 'test' of type 'FLOAT' cannot have a length"], Numeric("test", "FLOAT", length=5).schema_errors
        )
        self.assertEqual(
            [f"Column 'test' of type 'INT' must have an integer value as its length"],
            Numeric("test", "INT", length="5,2").schema_errors,
        )

    def test_character_set_errors(self):
        self.assertEqual(
            [f"Column 'test' of type 'INT' cannot have a character set"],
            Numeric("test", "INT", character_set="UTF-8").schema_errors,
        )
        self.assertEqual(
            [f"Column 'test' of type 'INT' cannot have a collate"],
            Numeric("test", "INT", collate="UTF-8").schema_errors,
        )

    def test_auto_increment_errors(self):
        self.assertEqual(
            [f"Column 'test' of type 'FLOAT' cannot be an AUTO_INCREMENT"],
            Numeric("test", "FLOAT", auto_increment=True).schema_errors,
        )
        self.assertEqual([], Numeric("test", "FLOAT", auto_increment=False).schema_errors)
        self.assertEqual([], Numeric("test", "INT", auto_increment=True).schema_errors)

    def test_integer_display_width_ignored(self):
        """MySQL 8.0.22+ strips display width from SHOW CREATE TABLE for integer types"""
        int_types = ["INT", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT"]
        for col_type in int_types:
            with_width = Numeric("col", col_type, length=1, null=False, default=0)
            without_width = Numeric("col", col_type, length=None, null=False, default=0)
            self.assertTrue(
                with_width.is_really_the_same_as(without_width), f"{col_type}(1) should equal {col_type} (no width)"
            )
            self.assertTrue(
                without_width.is_really_the_same_as(with_width), f"{col_type} should equal {col_type}(1) (reverse)"
            )

    def test_decimal_length_still_matters(self):
        col1 = Numeric("col", "DECIMAL", length="10,2", default="0.00")
        col2 = Numeric("col", "DECIMAL", length="5,2", default="0.00")
        self.assertFalse(col1.is_really_the_same_as(col2))
