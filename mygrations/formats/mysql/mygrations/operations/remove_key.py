class RemoveKey:
    """ Generates a partial SQL command to drop a key from a table """
    def __init__(self, key):
        self.key = key

    def apply_to_table(self, table):
        """ Removes the key from the table

        :param table: The table to remove the key from
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.remove_key(self.key)

    def __str__(self):
        if self.key.index_type == 'PRIMARY':
            return 'DROP PRIMARY KEY'
        return 'DROP KEY `%s`' % (self.key.name)
