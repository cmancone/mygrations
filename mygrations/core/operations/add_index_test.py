import unittest
from .add_index import AddIndex
from ..definitions.index import Index
class AddIndexTest(unittest.TestCase):
    def test_as_string(self):
        index = Index('user_id', ['user_id', 'account_id'], 'index')
        add_index = AddIndex(index)
        self.assertEquals("ADD KEY `user_id` (`user_id`,`account_id`)", str(add_index))
