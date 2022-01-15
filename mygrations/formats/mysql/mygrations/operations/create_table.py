class CreateTable:
    """ Generates an SQL command to create a table """
    def __init__(self, table, nice=False):
        """ Create table constructor

        :param table: The table to build a create table command for
        :param nice: Whether or not to return a nicely formatted CREATE TABLE command
        :type table: formats.mysql.definitions.table
        :type nice: bool
        """
        self.table = table
        self._nice = nice

    @property
    def table_name(self):
        """ Public getter.  Returns the name of the table.

        :returns: The table name
        :rtype: string
        """

        return self.table.name

    def __str__(self):
        newline = '\n' if self._nice else ''
        padding = '  ' if self._nice else ''
        body = ['%s%s' % (padding, str(self.table.columns[col])) for col in self.table.columns]
        body.extend(['%s%s' % (padding, str(self.table.indexes[index])) for index in self.table.indexes])
        body.extend([
            '%s%s' % (padding, str(self.table.constraints[constraint])) for constraint in self.table.constraints
        ])
        options = ['%s=%s' % (opt.name, opt.value) for opt in self.table.options]
        if options:
            options = ' %s' % ' '.join(options)
        else:
            options = ''
        return 'CREATE TABLE `%s` (%s%s%s)%s;' % (self.table.name, newline, ",\n".join(body), newline, options)
