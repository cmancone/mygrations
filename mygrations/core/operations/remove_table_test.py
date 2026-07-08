import unittest
from .remove_table import RemoveTable
class RemoveTableTest(unittest.TestCase):
    def test_as_string(self):
        self.assertEqual("DROP TABLE `test_table`;", str(RemoveTable('test_table')))
