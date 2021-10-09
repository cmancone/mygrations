from ..definitions.index import Index
from ..definitions.table import Table
class AddIndex:
    """ Generates a partial SQL command to add an index to a table """
    _index: Index = None

    def __init__(self, index: Index):
        self._index = index

    def apply_to_table(self, table: Table):
        """ Adds the index to the table """
        table.add_index(self._index)

    def __str__(self):
        return 'ADD %s' % str(self._index)
