class RemoveColumn:
    """ Generates a partial SQL command to remove a column from a table """
    def __init__(self, column):
        self.column = column

    def apply_to_table(self, table):
        """ Removes the column from the table

        :param table: The table to remove the column from
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.remove_column(self.column)

    def __str__(self):
        return 'DROP %s' % self.column.name
