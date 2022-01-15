from ..definitions.constraint import Constraint
from ..definitions.table import Table
class ChangeConstraint:
    """ Generates a partial SQL command to change a constraint in a table """
    def __init__(self, constraint: Constraint):
        self.constraint = constraint

    def apply_to_table(self, table: Table):
        """ Changes the constraint in the table """
        table.change_constraint(self.constraint)

    def __str__(self):
        return 'DROP FOREIGN KEY `%s`, ADD %s' % (self.constraint.name, str(self.constraint))
