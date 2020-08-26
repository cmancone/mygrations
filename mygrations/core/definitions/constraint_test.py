import unittest
from .constraint import Constraint


class TestConstraint(unittest.TestCase):
    def test_string_conversion(self):
        constraint = Constraint(
            column='user_id',
            name='user_id_fk',
            foreign_table='users',
            foreign_column='id',
            on_delete='SET NULL',
            on_update='CASCADE',
        )

        self.assertEquals(
            'CONSTRAINT `user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE',
            str(constraint)
        )
