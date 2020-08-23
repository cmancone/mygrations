import unittest
from .numeric import Numeric


class TestNumeric(unittest.TestCase):
    def test_is_the_same(self):
        attrs = {
            'name': 'test',
            'column_type': 'DECIMAL',
            'length': '5,2',
            'default': '0.00'
        }

        column1 = Numeric(**attrs)
        column2 = Numeric(**attrs)
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        column1 = Numeric(**attrs)
        column2 = Numeric(**{**attrs, 'default': '0.02'})
        self.assertFalse(column1.is_really_the_same_as(column2))
        self.assertFalse(column2.is_really_the_same_as(column1))

        column1 = Numeric(**attrs)
        column2 = Numeric(**{**attrs, 'default': '0.001'})
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        column1 = Numeric(**attrs)
        column2 = Numeric(**{**attrs, 'default': 0})
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))
