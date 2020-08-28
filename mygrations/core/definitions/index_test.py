import unittest
from .index import Index
from .columns.string import String


class TestIndex(unittest.TestCase):
    def test_string_conversion(self):
        name = String('name', 'VARCHAR')
        description = String('description', 'VARCHAR')

        index = Index('test_index', [name, description], index_type='UNIQUE')

        self.assertEquals(
            'UNIQUE KEY `test_index` (`name`,`description`)',
            str(index)
        )
