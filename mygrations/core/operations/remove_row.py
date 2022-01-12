from typing import Union
from ..definitions.table import Table
class RemoveRow:
    """ Generates an SQL command to delete a record """
    def __init__(self, table_name: Union[str, Table], row_id: Union[int, str]):
        if type(table_name) != str:
            self._table_name = table_name.name
        else:
            self._table_name = table_name
        self.row_id = row_id

    @property
    def table_name(self) -> str:
        """ Returns the name of the table. """
        return self._table_name

    def __str__(self):
        return "DELETE FROM `%s` WHERE id='%s';" % (self._table_name, self.row_id)
