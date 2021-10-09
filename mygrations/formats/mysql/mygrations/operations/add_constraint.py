class AddConstraint:
    """ Generates a partial SQL command to add a FK to a table """
    def __init__(self, constraint):
        self.constraint = constraint

    def apply_to_table(self, table):
        """ Adds the constraint to the table

        :param table: The table to add the constraint to
        :param type: mygrations.formats.mysql.definitions.table
        """
        table.add_constraint(self.constraint)

    def __str__(self):
        return 'ADD %s' % str(self.constraint)
