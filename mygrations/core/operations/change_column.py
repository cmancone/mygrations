from ..definitions.columns.column import Column
from ..definitions.table import Table
class ChangeColumn:
    """ Generates a partial SQL command to change a column in a table """
    def __init__(self, column: Column):
        self.column = column

    def apply_to_table(self, table: Table):
        """ Changes the column in the table """
        table.change_column(self.column)

    def __str__(self):
        return 'CHANGE `%s` %s' % (self.column.name, str(self.column))
