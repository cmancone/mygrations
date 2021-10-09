import unittest
from .change_column import ChangeColumn
from ..definitions.columns import String
class ChangeColumnTest(unittest.TestCase):
    def test_as_string(self):
        name = String('name', 'VARCHAR', length=255)
        self.assertEquals("CHANGE `name` `name` VARCHAR(255)", str(ChangeColumn(name)))
