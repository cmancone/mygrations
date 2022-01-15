from typing import Union, Dict
from ..definitions.table import Table
class AddRow:
    """ Generates an SQL command to insert a record """
    def __init__(self, table_name: Union[str, Table], data: Dict):
        if type(table_name) != str:
            self._table_name = table_name.name
        else:
            self._table_name = table_name
        self._data = data

    @property
    def table_name(self) -> str:
        """ Returns the name of the table. """
        return self._table_name

    def __str__(self):
        cols = ', '.join(['`%s`' % val for val in self._data.keys()])
        vals = ', '.join([
            "'%s'" % str(val).replace('\\', '\\\\').replace("'", "\\'") if val is not None else 'NULL'
            for val in self._data.values()
        ])
        return 'INSERT INTO `%s` (%s) VALUES (%s);' % (self._table_name, cols, vals)
