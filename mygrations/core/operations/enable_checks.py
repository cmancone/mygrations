class EnableChecks:
    """ Generates an SQL command to re-enable foreign key checks """
    def __str__(self):
        return 'SET FOREIGN_KEY_CHECKS=1;'
