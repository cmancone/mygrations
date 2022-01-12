class RowUpdate:
    """ Generates an SQL command to update a record """
    def __init__(self, table_name, data):
        if 'id' not in data:
            raise KeyError('Missing `id` column needed for update')

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
        updates = ', '.join([
            "`%s`='%s'" % (key, str(val).replace('\\', '\\\\')) if val is not None else ('`%s`=NULL' % key)
            for (key, val) in self.data.items() if key != 'id'
        ])
        return "UPDATE `%s` SET %s WHERE id='%s';" % (self._table_name, updates, self.data['id'])
