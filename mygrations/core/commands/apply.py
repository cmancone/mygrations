from .plan import Plan
def execute(options, print_results=True):

    obj = Apply(options)
    return obj.execute(print_results=print_results)
class Apply(Plan):
    needs_cursor = False

    def execute(self, print_results):

        commands = self.build_commands()
        to_apply = ['%s' % command for command in commands]
        connection = self.get_driver()
        connection.execute(to_apply)
        if print_results:
            if to_apply:
                print('Applied:')
                print("\n".join(to_apply))
            else:
                print('No changes required')
        return (to_apply, True)
