from .plan import Plan
def execute(options):

    obj = Apply(options)
    obj.execute()
class Apply(Plan):
    needs_cursor = False

    def execute(self):

        commands = self.build_commands()
        connection = self.get_driver()
        connection.execute(['%s' % command for command in commands])
