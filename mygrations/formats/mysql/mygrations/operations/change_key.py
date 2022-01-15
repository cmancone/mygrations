class ChangeKey:
    """ Generates a partial SQL command to change a key in a table """
    def __init__(self, key):
        self.key = key

    def apply_to_table(self, table):
        """ Changes the key in the table

        :param table: The table to change the key on
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.change_key(self.key)

    def __str__(self):
        return 'DROP KEY `%s`, ADD %s' % (self.key.name, str(self.key))
