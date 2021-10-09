from .plan import Plan
from mygrations.drivers.mysqldb.mysqldb import mysqldb
def execute(options):

    obj = Apply(options)
    obj.execute()
class Apply(Plan):
    def execute(self):

        commands = self.build_commands()
        connection = mysqldb(self.credentials)
        connection.execute(['%s' % command for command in commands])
