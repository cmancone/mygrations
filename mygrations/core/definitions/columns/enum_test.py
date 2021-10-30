import unittest
from .enum import Enum
class TestString(unittest.TestCase):
    def test_string_conversion(self):
        column = Enum('test_column', 'ENUM', values=['asdf', 'qwerty'], default='qwerty')

        self.assertEquals("`test_column` ENUM('asdf', 'qwerty') DEFAULT \'qwerty\'", str(column))
        self.assertEquals([], column.errors)
        self.assertEquals([], column.warnings)

    def test_default_errors(self):
        column = Enum('test_column', 'ENUM', values=['asdf', 'qwerty'], default='adf')
        self.assertEquals(["Default value for 'ENUM' column 'test_column' is not in the list of allowed values"],
                          column.errors)

        self.assertEquals([], Enum('test_column', 'ENUM', values=['asdf', 'qwerty']).errors)
