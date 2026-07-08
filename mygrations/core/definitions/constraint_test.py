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

        self.assertEqual('user_id_fk', constraint.name)
        self.assertEqual('user_id', constraint.column_name)
        self.assertEqual('users', constraint.foreign_table_name)
        self.assertEqual('id', constraint.foreign_column_name)
        self.assertEqual('RESTRICT', constraint.on_delete)
        self.assertEqual('RESTRICT', constraint.on_update)
        self.assertEqual([], constraint.schema_errors)

    def test_action(self):
        constraint = Constraint(
            'user_id_fk',
            'user_id',
            'users',
            'id',
            on_delete='GARBAGE',
            on_update='whatever',
        )
        self.assertEqual([
            "ON DELETE action of 'GARBAGE' for constraint 'user_id_fk' is not a valid ON DELETE action",
            "ON UPDATE action of 'WHATEVER' for constraint 'user_id_fk' is not a valid ON UPDATE action",
        ], constraint.schema_errors)
