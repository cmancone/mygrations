import unittest
from .remove_column import RemoveColumn
from ..definitions.columns import String
class RemoveColumnTest(unittest.TestCase):
    def test_as_string(self):
        string = String('name', 'VARCHAR', length=255, default='', null=False)
        self.assertEquals("DROP `name`", str(RemoveColumn(string)))
