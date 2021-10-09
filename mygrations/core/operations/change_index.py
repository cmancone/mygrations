from ..definitions.index import Index
from ..definitions.table import Table
class ChangeIndex:
    """ Generates a partial SQL command to change an index in a table """
    def __init__(self, index: Index):
        self.index = index

    def apply_to_table(self, table: Table):
        """ Changes the index in the table """
        table.change_index(self.index)

    def __str__(self):
        return 'DROP KEY `%s`, ADD %s' % (self.index.name, str(self.index))
