from ..definitions.constraint import Constraint
from ..definitions.table import Table
class AddConstraint:
    """ Generates a partial SQL command to add a FK to a table """
    _constraint: Constraint = None

    def __init__(self, constraint: Constraint):
        self._constraint = constraint

    def apply_to_table(self, table: Table):
        """ Adds the constraint to the table """
        table.add_constraint(self._constraint)

    def __str__(self):
        return 'ADD %s' % str(self._constraint)
