import unittest
from .add_row import AddRow
from collections import OrderedDict
class AddRowTest(unittest.TestCase):
    def test_as_string(self):
        row = OrderedDict([('id', 10), ('age', '5'), ('dob', None)])
        add_row = AddRow('test_table', row)
        self.assertEquals("INSERT INTO `test_table` (`id`, `age`, `dob`) VALUES ('10', '5', NULL);", str(add_row))
