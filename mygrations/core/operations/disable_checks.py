class DisableChecks:
    """ Generates an SQL command to disable foreign key checks """
    def __str__(self):
        return 'SET FOREIGN_KEY_CHECKS=0;'
