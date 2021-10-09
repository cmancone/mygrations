class RemoveConstraint:
    """ Generates a partial SQL command to drop a foreign key from a table """
    def __init__(self, constraint):
        self.constraint = constraint

    def apply_to_table(self, table):
        """ Removes the constraint from the table

        :param table: The table to remove the constraint from
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.remove_constraint(self.constraint)

    def __str__(self):
        return 'DROP FOREIGN KEY `%s`' % (self.constraint.name)
