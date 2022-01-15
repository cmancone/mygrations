import unittest
from .add_constraint import AddConstraint
from ..definitions.constraint import Constraint
class AddConstraintTest(unittest.TestCase):
    def test_as_string(self):
        constraint = Constraint('user_id_fk', 'user_id', 'users', 'id')
        add_constraint = AddConstraint(constraint)
        self.assertEquals(
            "ADD CONSTRAINT `user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT",
            str(add_constraint)
        )
