from ..definitions.index import Index
from ..definitions.table import Table
class RemoveIndex:
    """ Generates a partial SQL command to drop an index from a table """
    def __init__(self, index: Index):
        self._index = index

    def apply_to_table(self, table: Table):
        """ Removes the index from the table """
        table.remove_index(self._index)

    def __str__(self):
        if self._index.index_type == 'PRIMARY':
            return 'DROP PRIMARY KEY'
        return 'DROP KEY `%s`' % (self._index.name)
