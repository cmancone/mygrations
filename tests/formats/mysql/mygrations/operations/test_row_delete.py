import unittest
from mygrations.formats.mysql.mygrations.operations.row_delete import row_delete
from collections import OrderedDict
class test_row_delete(unittest.TestCase):
    def test_simple(self):
        op = row_delete('a_table', 7)

        self.assertEquals("DELETE FROM `a_table` WHERE id=7;", str(op))
        self.assertEquals('a_table', op.table_name)
