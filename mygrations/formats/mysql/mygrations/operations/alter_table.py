class AlterTable:
    """ Generates an SQL command to alter a table """
    def __init__(self, table):
        self._table = table
        self._operations = []

    def add_operation(self, operation):
        self._operations.append(operation)

    @property
    def table_name(self):
        """ Public getter.  Returns the name of the table.

        :returns: The table name
        :rtype: string
        """

        return self._table

    def __len__(self):
        return len(self._operations)

    def __bool__(self):
        return True if len(self._operations) else False

    def __str__(self):
        return 'ALTER TABLE `%s` %s;' % (self._table, ', '.join([str(x) for x in self._operations]))

    def __iter__(self):
        return self._operations.__iter__()
