import unittest
from collections import OrderedDict
from .columns import Numeric, String
from .constraint import Constraint
from .index import Index
from .option import Option
from .table import Table


class TestTable(unittest.TestCase):
    def setUp(self):
        self.id = Numeric('id', 'INT', length=10, unsigned=True, null=False, auto_increment=True)
        self.user_id = Numeric('user_id', 'INT', length=10, unsigned=True, null=False)
        self.age = Numeric('age', 'INT', length=10, unsigned=True, default=0)
        self.name = String('name', 'VARCHAR', length=255, default='', null=False)
        self.id_index = Index('id_index', ['id'], 'PRIMARY')
        self.name_age_index = Index('name_age', ['name', 'age'], 'INDEX')
        self.user_id_index = Index('user_id_index', ['user_id'], 'INDEX')
        self.user_id_constraint = Constraint('user_id_fk', 'user_id', 'users', 'id', 'SET NULL', 'SET NULL')
        self.engine = Option('ENGINE', 'InnoDB')

    def test_can_create(self):
        table = Table(
            'registrations',
            [self.id, self.user_id, self.age, self.name],
            [self.user_id_constraint],
            [self.id_index, self.name_age_index, self.user_id_index],
            [self.engine],
        )

        self.assertEquals('registrations', table.name)
        self.assertEquals(
            ['id', 'user_id', 'age', 'name'],
            [column.name for column in table.columns.values()]
        )
        self.assertEquals(
            ['user_id_fk'],
            [constraint.name for constraint in table.constraints.values()]
        )
        self.assertEquals(
            ['id_index', 'name_age', 'user_id_index'],
            [index.name for index in table.indexes.values()]
        )
        self.assertEquals([self.engine], table.options)
        self.assertEquals(self.id_index, table.primary)
