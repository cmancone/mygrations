class ChangeConstraint:
    """ Generates a partial SQL command to change a foreign key in a table """
    def __init__(self, constraint):
        self.constraint = constraint

    def apply_to_table(self, table):
        """ Changes the constraint in the table

        :param table: The table to change the constraint on
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.change_constraint(self.constraint)

    def __str__(self):
        return 'DROP FOREIGN KEY `%s`, ADD %s' % (self.constraint.name, str(self.constraint))
