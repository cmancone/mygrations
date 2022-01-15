import unittest
from .change_index import ChangeIndex
from ..definitions.index import Index
class ChangeIndexTest(unittest.TestCase):
    def test_as_string(self):
        index = Index('user_id', ['user_id', 'account_id'], 'index')
        self.assertEquals("DROP KEY `user_id`, ADD KEY `user_id` (`user_id`,`account_id`)", str(ChangeIndex(index)))
