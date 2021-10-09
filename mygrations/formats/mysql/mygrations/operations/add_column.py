class AddColumn:
    """ Generates a partial SQL command to add a column to a table """
    def __init__(self, column, position=None):
        """ Create an add column operation

        Position should be one of:

        ==================  ====================
        Value               Meaning
        ==================  ====================
        None                Put at the end of the table
        False               Put at the end of the table
        True                Put at the beginning of the table
        Any string          position should be a column name: put the new column after that one
        ==================  ====================

        :param column: The column to add
        :param position: Where to put the new column in the table
        :type column: mygrations.formats.mysql.definitions.column
        :type position: mixed:
        """

        self.column = column
        self.position = position

    def apply_to_table(self, table):
        """ Adds the column to the table

        :param table: The table to add the column to
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.add_column(self.column, self.position)

    def __str__(self):
        basic = 'ADD %s' % self.column
        if self.position == True:
            position = ' FIRST'
        elif type(self.position) == type(''):
            position = ' AFTER `%s`' % self.position
        else:
            position = ''

        return 'ADD %s%s' % (str(self.column), position)
