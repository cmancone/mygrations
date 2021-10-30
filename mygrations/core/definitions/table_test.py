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
            [self.id_index, self.name_age_index, self.user_id_index],
            [self.user_id_constraint],
            [self.engine],
        )

        self.assertEquals('registrations', table.name)
        self.assertEquals(['id', 'user_id', 'age', 'name'], [column.name for column in table.columns.values()])
        self.assertEquals(['user_id_fk'], [constraint.name for constraint in table.constraints.values()])
        self.assertEquals(['id_index', 'name_age', 'user_id_index'], [index.name for index in table.indexes.values()])
        self.assertEquals([self.engine], table.options)
        self.assertEquals(self.id_index, table.primary)
        self.assertEquals([], table.errors)

    def test_require_basics(self):
        table = Table('', [self.id], [self.id_index], [], [])
        self.assertEquals(["Table missing name"], table.errors)

        table = Table('no_cols', [], [], [], [])
        self.assertEquals(["Table 'no_cols' does not have any columns"], table.errors)

    def test_include_child_errors(self):
        bad_column = String('text', 'TEXT', default='')
        bad_index = Index('no_cols', [], 'INDEX')
        bad_constraint = Constraint('user_id_fk', 'user_id', 'users', 'id', on_delete='CASCAD')
        table = Table(
            'errors',
            [self.id, self.user_id, bad_column],
            [self.id_index, bad_index],
            [bad_constraint],
            [self.engine],
        )
        self.assertEquals([
            "Column text of type TEXT cannot have a default in table 'errors'",
            "Missing columns for index no_cols in table 'errors'",
            "ON DELETE action of 'CASCAD' for constraint user_id_fk is not a valid ON DELETE action in table 'errors'",
        ], table.errors)

    def test_duplicates(self):
        table = Table('errors', [self.id, self.id], [self.id_index], [], [])
        self.assertEquals([
            "Duplicate column name found in table 'errors': 'id'",
            "Table 'errors' has more than one AUTO_INCREMENT column",
        ], table.errors)

        table = Table('errors', [self.id], [self.id_index, Index('id_index', ['id'], 'INDEX')], [], [])
        self.assertEquals(["Duplicate index name found in table 'errors': 'id_index'"], table.errors)

        table = Table(
            'errors', [self.id, self.user_id], [self.id_index, self.user_id_index],
            [self.user_id_constraint, self.user_id_constraint], []
        )
        self.assertEquals(["Duplicate constraint name found in table 'errors': 'user_id_fk'"], table.errors)

    def test_check_primaries(self):
        table = Table('errors', [self.id], [self.id_index, Index('id_primary', ['id'], 'PRIMARY')], [], [])
        self.assertEquals(["Table 'errors' has more than one PRIMARY index"], table.errors)

        table = Table('errors', [self.id], [], [], [])
        self.assertEquals(["Table 'errors' has an AUTO_INCREMENT column but is missing the PRIMARY index"],
                          table.errors)

        table = Table(
            'errors',
            [self.id, self.user_id],
            [Index('user_id', ['user_id'], 'PRIMARY')],
            [],
            [],
        )
        self.assertEquals([
            "Mismatched indexes in table 'errors': column 'id' is the AUTO_INCREMENT column but 'user_id' is the PRIMARY index column"
        ], table.errors)

    def test_check_missing_index_columns(self):
        table = Table(
            'errors', [self.id, self.user_id],
            [self.id_index, Index('bad_index', ['non_column'], 'INDEX')], [], []
        )
        self.assertEquals(["Table 'errors' has index 'bad_index' that references non-existent column 'non_column'"],
                          table.errors)