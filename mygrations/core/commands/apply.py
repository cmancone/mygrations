from .plan import Plan
from mygrations.drivers.pymysql.pymysql import PyMySQL
def execute(options):

    obj = Apply(options)
    obj.execute()
class Apply(Plan):
    needs_cursor = False
    def execute(self):

        commands = self.build_commands()
        connection = self.get_cursor()
        connection.execute(['%s' % command for command in commands])
