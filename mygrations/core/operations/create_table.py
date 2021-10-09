class CreateTable:
    """ Generates an SQL command to create a table """
    _table = None
    _nice: bool

    def __init__(self, table, nice=False):
        self._table = table
        self._nice = nice

    @property
    def table_name(self) -> str:
        """ Returns the name of the table. """
        return self._table.name

    def __str__(self):
        newline = '\n' if self._nice else ''
        padding = '  ' if self._nice else ''
        body_separator = ',\n' if self._nice else ','
        body = ['%s%s' % (padding, str(self._table.columns[col])) for col in self._table.columns]
        body.extend(['%s%s' % (padding, str(self._table.indexes[index])) for index in self._table.indexes])
        body.extend([
            '%s%s' % (padding, str(self._table.constraints[constraint])) for constraint in self._table.constraints
        ])
        options = ['%s=%s' % (opt.name, opt.value) for opt in self._table.options]
        if options:
            options = ' %s' % ' '.join(options)
        else:
            options = ''
        return 'CREATE TABLE `%s` (%s%s%s)%s;' % (
            self._table.name, newline, body_separator.join(body), newline, options
        )
