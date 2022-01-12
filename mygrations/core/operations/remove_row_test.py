import unittest
from .remove_row import RemoveRow
class RemoveRowTest(unittest.TestCase):
    def test_as_string(self):
        self.assertEquals("DELETE FROM `test_table` WHERE id='10';", str(RemoveRow('test_table', 10)))
