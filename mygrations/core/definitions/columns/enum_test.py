import unittest
from .enum import Enum
class TestEnum(unittest.TestCase):
    def test_string_conversion(self):
        column = Enum('test_column', 'ENUM', enum_values=['asdf', 'qwerty'], default='qwerty')

        self.assertEquals("`test_column` ENUM('asdf', 'qwerty') DEFAULT \'qwerty\'", str(column))
        self.assertEquals([], column.schema_errors)
        self.assertEquals([], column.schema_warnings)

    def test_default_errors(self):
        column = Enum('test_column', 'ENUM', enum_values=['asdf', 'qwerty'], default='adf')
        self.assertEquals(["Default value for 'ENUM' column 'test_column' is not in the list of allowed values"],
                          column.schema_errors)

        self.assertEquals([], Enum('test_column', 'ENUM', enum_values=['asdf', 'qwerty']).schema_errors)
