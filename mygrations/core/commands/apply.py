from .plan import plan
from mygrations.drivers.mysqldb.mysqldb import mysqldb
def execute(options):

    obj = apply(options)
    obj.execute()
class apply(plan):
    def execute(self):

        commands = self.build_commands()
        connection = mysqldb(self.credentials)
        connection.execute(['%s' % command for command in commands])
