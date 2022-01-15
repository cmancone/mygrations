from typing import Union
from ..definitions.columns.column import Column
from ..definitions.table import Table
class AddColumn:
    _column: Column
    _position: Union[str, bool] = None
    """ Generates a partial SQL command to add a column to a table """
    def __init__(self, column: Column, position: Union[str, bool] = None):
        """ Create an add column operation

        Position should be one of:

        ==================  ====================
        Value               Meaning
        ==================  ====================
        None                Put at the end of the table
        False               Put at the end of the table
        True                Put at the beginning of the table
        Any string          position should be a column name: put the new column after that one
        ==================  ====================

        :param column: The column to add
        :param position: Where to put the new column in the table
        :type column: mygrations.formats.mysql.definitions.column
        :type position: mixed:
        """
        self._column = column
        self._position = position

    def apply_to_table(self, table: Table):
        """ Adds the column to the table """
        table.add_column(self._column, self._position)

    def __str__(self):
        if self._position == True:
            position = ' FIRST'
        elif type(self._position) == str:
            position = ' AFTER `%s`' % self._position
        else:
            position = ''

        return 'ADD %s%s' % (str(self._column), position)
