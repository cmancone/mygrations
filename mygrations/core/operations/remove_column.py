from ..definitions.columns.column import Column
from ..definitions.table import Table
class RemoveColumn:
    """ Generates a partial SQL command to remove a column from a table """
    def __init__(self, column: Column):
        self._column = column

    def apply_to_table(self, table: Table):
        """ Removes the column from the table """
        table.remove_column(self.column)

    def __str__(self):
        return 'DROP `%s`' % self._column.name
