import unittest
from .constraint import Constraint
class TestConstraint(unittest.TestCase):
    def test_can_create(self):
        constraint = Constraint(
            'user_id_fk',
            'user_id',
            'users',
            'id',
        )

        self.assertEquals('user_id_fk', constraint.name)
        self.assertEquals('user_id', constraint.column_name)
        self.assertEquals('users', constraint.foreign_table_name)
        self.assertEquals('id', constraint.foreign_column_name)
        self.assertEquals('RESTRICT', constraint.on_delete)
        self.assertEquals('RESTRICT', constraint.on_update)
        self.assertEquals([], constraint.schema_errors)

    def test_action(self):
        constraint = Constraint(
            'user_id_fk',
            'user_id',
            'users',
            'id',
            on_delete='GARBAGE',
            on_update='whatever',
        )
        self.assertEquals([
            "ON DELETE action of 'GARBAGE' for constraint 'user_id_fk' is not a valid ON DELETE action",
            "ON UPDATE action of 'WHATEVER' for constraint 'user_id_fk' is not a valid ON UPDATE action",
        ], constraint.schema_errors)
