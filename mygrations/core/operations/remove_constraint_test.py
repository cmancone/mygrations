import unittest
from .remove_constraint import RemoveConstraint
from ..definitions.constraint import Constraint
class RemoveConstraintTest(unittest.TestCase):
    def test_as_string(self):
        constraint = Constraint('user_id_fk', 'user_id', 'users', 'id')
        self.assertEquals("DROP FOREIGN KEY `user_id_fk`", str(RemoveConstraint(constraint)))
