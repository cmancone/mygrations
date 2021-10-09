import unittest
from .remove_index import RemoveIndex
from ..definitions.index import Index
class RemoveIndexTest(unittest.TestCase):
    def test_as_string(self):
        index = Index('user_id', ['user_id', 'account_id'], 'index')
        self.assertEquals("DROP KEY `user_id`", str(RemoveIndex(index)))

        index = Index('user_id', ['user_id'], 'primary')
        self.assertEquals("DROP PRIMARY KEY", str(RemoveIndex(index)))
