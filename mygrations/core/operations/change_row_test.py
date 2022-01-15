import unittest
from .change_row import ChangeRow
from collections import OrderedDict
class ChangeRowTest(unittest.TestCase):
    def test_as_string(self):
        row = OrderedDict([('id', 10), ('age', '5'), ('dob', None)])
        change_row = ChangeRow('test_table', row)
        self.assertEquals("UPDATE `test_table` SET `age`='5', `dob`=NULL WHERE id='10';", str(change_row))
