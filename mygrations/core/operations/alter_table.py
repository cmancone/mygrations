class AlterTable:
    """ Generates an SQL command to alter a table """
    def __init__(self, table_name: str):
        self._table_name = table_name
        self._operations = []

    def add_operation(self, operation):
        self._operations.append(operation)

    @property
    def table_name(self) -> str:
        """ Returns the name of the table. """
        return self._table_name

    def __len__(self):
        return len(self._operations)

    def __bool__(self):
        return True if len(self._operations) else False

    def __str__(self):
        return 'ALTER TABLE `%s` %s;' % (self.table_name, ', '.join([str(x) for x in self._operations]))

    def __iter__(self):
        return self._operations.__iter__()
