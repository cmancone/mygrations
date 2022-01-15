from ..definitions.constraint import Constraint
from ..definitions.table import Table
class RemoveConstraint:
    """ Generates a partial SQL command to drop a foreign key from a table """
    def __init__(self, constraint: Constraint):
        self._constraint = constraint

    def apply_to_table(self, table: Table):
        """ Removes the constraint from the table """
        table.remove_constraint(self._constraint)

    def __str__(self):
        return 'DROP FOREIGN KEY `%s`' % (self._constraint.name)
