import unittest
from .remove_table import RemoveTable
from ..definitions.columns import String, Numeric
from ..definitions.index import Index
from ..definitions.table import Table
from ..definitions.option import Option


class RemoveTableTest(unittest.TestCase):
    def test_as_string(self):
        self.assertEquals("DROP TABLE `test_table`;", str(RemoveTable('test_table')))
