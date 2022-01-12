class RowDelete:
    """ Generates an SQL command to delete a record """
    def __init__(self, table_name, row_id):
        if type(table_name) != str:
            self._table_name = table_name.name
        else:
            self._table_name = table_name
        self.row_id = row_id

    @property
    def table_name(self):
        """ Public getter.  Returns the name of the table.

        :returns: The table name
        :rtype: string
        """

        return self._table_name

    def __str__(self):
        return "DELETE FROM `%s` WHERE id='%s';" % (self._table_name, self.row_id)
