from .plan import Plan
from mygrations.drivers.pymysql.pymysql import PyMySQL
def execute(options):

    obj = Apply(options)
    obj.execute()
class Apply(Plan):
    def execute(self):

        commands = self.build_commands()
        connection = PyMySQL(self.credentials)
        connection.execute(['%s' % command for command in commands])
