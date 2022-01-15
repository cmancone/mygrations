class RowInsert:
    """ Generates an SQL command to insert a record """
    def __init__(self, table_name, data):
        if type(table_name) != str:
            self._table_name = table_name.name
        else:
            self._table_name = table_name
        self.data = data

    @property
    def table_name(self):
        """ Public getter.  Returns the name of the table.

        :returns: The table name
        :rtype: string
        """

        return self._table_name

    def __str__(self):
        cols = ', '.join(['`%s`' % val for val in self.data.keys()])
        vals = ', '.join([
            "'%s'" % str(val).replace('\\', '\\\\').replace("'", "\\'") if val is not None else 'NULL'
            for val in self.data.values()
        ])
        return 'INSERT INTO `%s` (%s) VALUES (%s);' % (self._table_name, cols, vals)
