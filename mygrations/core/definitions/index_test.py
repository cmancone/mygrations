import unittest
from .index import Index
from .columns.string import String
class TestIndex(unittest.TestCase):
    def setUp(self):
        self.columns = ['name', 'description']

    def test_can_create(self):
        name = String('name', 'VARCHAR')
        description = String('description', 'VARCHAR')
        index = Index('test_index', self.columns, index_type='unique')

        self.assertEquals('test_index', index.name)
        self.assertEquals('UNIQUE', index.index_type)
        self.assertEquals(self.columns, index.columns)
        self.assertEquals([], index.errors)

    def test_string_conversion(self):
        index = Index('test_index', self.columns, index_type='UNIQUE')

        self.assertEquals('UNIQUE KEY `test_index` (`name`,`description`)', str(index))

    def test_name_too_long(self):
        too_long = '012345678901234567890123456789012345678901234567890123456789012345'
        index = Index(too_long, self.columns, index_type='UNIQUE')
        self.assertEquals([f'Key name {too_long} must be <=64 characters long'], index.errors)
