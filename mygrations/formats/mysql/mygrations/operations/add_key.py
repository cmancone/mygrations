class AddKey:
    """ Generates a partial SQL command to add a key to a table """
    def __init__(self, key):
        self.key = key

    def apply_to_table(self, table):
        """ Adds the key to the table

        :param table: The table to add the key to
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.add_key(self.key)

    def __str__(self):
        return 'ADD %s' % str(self.key)
