import unittest
from .numeric import Numeric
class NumericTest(unittest.TestCase):
    def test_is_the_same(self):
        attrs = {'length': '5,2', 'default': '0.00'}

        column1 = Numeric('test', 'DECIMAL', **attrs)
        column2 = Numeric('test', 'DECIMAL', **attrs)
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        column1 = Numeric('test', 'DECIMAL', **attrs)
        column2 = Numeric('test', 'DECIMAL', **{**attrs, 'default': '0.02'})
        self.assertFalse(column1.is_really_the_same_as(column2))
        self.assertFalse(column2.is_really_the_same_as(column1))

        column1 = Numeric('test', 'DECIMAL', **attrs)
        column2 = Numeric('test', 'DECIMAL', **{**attrs, 'default': '0.001'})
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        column1 = Numeric('test', 'DECIMAL', **attrs)
        column2 = Numeric('test', 'DECIMAL', **{**attrs, 'default': 0})
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

    def test_default_errors(self):
        self.assertEquals([f"Column 'test' of type 'DECIMAL' cannot have a string value as a default"],
                          Numeric('test', 'DECIMAL', default='').schema_errors)
        self.assertEquals([f"Column 'test' of type 'INT' must have an integer value as a default"],
                          Numeric('test', 'INT', default=5.0).schema_errors)
        self.assertEquals([f"Column 'test' of type 'BIT' must have a default of 1 or 0"],
                          Numeric('test', 'BIT', default=5).schema_errors)
        self.assertEquals([], Numeric('test', 'BIT', default=1).schema_errors)
        self.assertEquals([], Numeric('test', 'INT', default=5).schema_errors)
        self.assertEquals([], Numeric('test', 'FLOAT', default=5.0).schema_errors)

    def test_length_errors(self):
        self.assertEquals([f"Column 'test' of type 'FLOAT' cannot have a length"],
                          Numeric('test', 'FLOAT', length=5).schema_errors)
        self.assertEquals([f"Column 'test' of type 'INT' must have an integer value as its length"],
                          Numeric('test', 'INT', length='5,2').schema_errors)

    def test_character_set_errors(self):
        self.assertEquals([f"Column 'test' of type 'INT' cannot have a character set"],
                          Numeric('test', 'INT', character_set='UTF-8').schema_errors)
        self.assertEquals([f"Column 'test' of type 'INT' cannot have a collate"],
                          Numeric('test', 'INT', collate='UTF-8').schema_errors)

    def test_auto_increment_errors(self):
        self.assertEquals([f"Column 'test' of type 'FLOAT' cannot be an AUTO_INCREMENT"],
                          Numeric('test', 'FLOAT', auto_increment=True).schema_errors)
        self.assertEquals([], Numeric('test', 'FLOAT', auto_increment=False).schema_errors)
        self.assertEquals([], Numeric('test', 'INT', auto_increment=True).schema_errors)
