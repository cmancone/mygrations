import unittest
from .column import Column
class MockColumn(Column):
    _allowed_column_types = ['INT']
class TestColumn(unittest.TestCase):
    def test_string_conversion(self):
        column = MockColumn(
            'test_column',
            'INT',
            length=25,
            null=False,
            default=0,
            unsigned=True,
        )

        self.assertEquals('`test_column` INT(25) UNSIGNED NOT NULL DEFAULT 0', str(column))

    def test_is_the_same(self):
        attrs = {
            'length': 5,
            'null': False,
            'unsigned': True,
            'default': '5',
        }
        column1 = MockColumn('test_column', 'INT', **attrs)
        column2 = MockColumn('test_column', 'INT', **attrs)

        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        diff = {
            'length': 6,
            'null': None,
            'unsigned': False,
            'default': 5,
        }
        for (key, val) in diff.items():
            column1 = MockColumn('test_column', 'INT', **attrs)
            column2 = MockColumn('test_column', 'INT', **{**attrs, **{key: val}})
            self.assertFalse(column1.is_really_the_same_as(column2))
            self.assertFalse(column2.is_really_the_same_as(column1))

        column1 = MockColumn('test_column', 'INT', **attrs)
        column2 = MockColumn('test_column', 'INT', **{**attrs, 'default': None})
        self.assertFalse(column1.is_really_the_same_as(column2))
        self.assertFalse(column2.is_really_the_same_as(column1))

    def test_not_null_needs_default(self):
        column = MockColumn(
            'test_column',
            'INT',
            length=25,
            null=False,
            default=None,
        )
        self.assertEquals(
            [
                'Column test_column does not allow null values and has no default: you should set a default to avoid warnings'
            ],
            column.schema_warnings,
        )

        column = MockColumn('test_column', 'INT')
        self.assertEquals([], column.schema_warnings)
