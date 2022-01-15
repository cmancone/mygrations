import unittest
from .constraint import Constraint
class TestConstraint(unittest.TestCase):
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
        self.assertEquals([], constraint.schema_errors)
        self.assertEquals([], constraint.schema_warnings)
