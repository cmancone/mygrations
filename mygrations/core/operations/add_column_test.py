import unittest
from .add_column import AddColumn
from ..definitions.columns import String
class AddColumnTest(unittest.TestCase):
    def test_as_string(self):
        string = String('name', 'VARCHAR', length=255, default='', null=False)
        add_column = AddColumn(string, 'age')
        self.assertEquals("ADD `name` VARCHAR(255) NOT NULL DEFAULT '' AFTER `age`", str(add_column))
