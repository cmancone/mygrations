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
        self.assertEquals('users', constraint.foreign_table)
        self.assertEquals('id', constraint.foreign_column_name)
        self.assertEquals('RESTRICT', constraint.on_delete)
        self.assertEquals('RESTRICT', constraint.on_update)
        self.assertEquals([], constraint.errors)

    def test_string_conversion(self):
        constraint = Constraint(
            'user_id_fk',
            'user_id',
            'users',
            'id',
            on_delete='SET NULL',
            on_update='CASCADE',
        )

        self.assertEquals(
            'CONSTRAINT `user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE',
            str(constraint)
        )
        self.assertEquals([], constraint.errors)

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
            "ON DELETE action of 'GARBAGE' for constraint user_id_fk is not a valid ON DELETE action",
            "ON UPDATE action of 'WHATEVER' for constraint user_id_fk is not a valid ON UPDATE action",
        ], constraint.errors)
