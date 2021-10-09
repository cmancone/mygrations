class ChangeColumn:
    """ Generates a partial SQL command to change a column in a table """
    def __init__(self, column):
        self.column = column

    def apply_to_table(self, table):
        """ Changes the column in the table

        :param table: The table to change the column on
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.change_column(self.column)

    def __str__(self):
        return 'CHANGE `%s` %s' % (self.column.name, str(self.column))
