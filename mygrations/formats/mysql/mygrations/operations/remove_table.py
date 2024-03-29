class RemoveTable:
    """ Generates an SQL command to drop a table """
    def __init__(self, table_name):
        if type(table_name) != str:
            self._table_name = table_name.name
        else:
            self._table_name = table_name

    @property
    def table_name(self):
        """ Public getter.  Returns the name of the table.

        :returns: The table name
        :rtype: string
        """

        return self._table_name

    def __str__(self):
        return 'DROP TABLE %s;' % self._table_name
