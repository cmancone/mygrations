import unittest
from .change_constraint import ChangeConstraint
from ..definitions.constraint import Constraint
class ChangeConstraintTest(unittest.TestCase):
    def test_as_string(self):
        constraint = Constraint('user_id_fk', 'user_id', 'users', 'id', on_update='cascade')
        self.assertEquals(
            "DROP FOREIGN KEY `user_id_fk`, ADD CONSTRAINT `user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE",
            str(ChangeConstraint(constraint))
        )
