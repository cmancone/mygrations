import unittest
from .column import Column


class MockColumn(Column):
    pass

class TestColumn(unittest.TestCase):
    def test_string_conversion(self):
        column = MockColumn(
            name='test_column',
            column_type='INT',
            length=25,
            null=False,
            default=0,
            unsigned=True,
        )

        self.assertEquals('`test_column` INT(25) UNSIGNED NOT NULL DEFAULT 0', str(column))

    def test_is_the_same(self):
        attrs = {
            'name': 'test',
            'column_type': 'INT',
            'length': 5,
            'null': False,
            'unsigned': True,
            'default': '5',
        }
        column1 = MockColumn(**attrs)
        column2 = MockColumn(**attrs)

        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        diff = {
            'name': 'test2',
            'length': 6,
            'null': None,
            'unsigned': False,
            'default': 5,
        }
        for (key,val) in diff.items():
            column1 = MockColumn(**attrs)
            column2 = MockColumn(**{**attrs, **{key: val}})
            self.assertFalse(column1.is_really_the_same_as(column2))
            self.assertFalse(column2.is_really_the_same_as(column1))

        column1 = MockColumn(**attrs)
        column2 = MockColumn(**{**attrs, 'default': None})
        self.assertFalse(column1.is_really_the_same_as(column2))
        self.assertFalse(column2.is_really_the_same_as(column1))
