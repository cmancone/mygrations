__ver__ = '1.0'

from .core import commands
class mygrate:

    command = ''
    options = None
    config = None

    def __init__(self, command, options={}):

        # store the name of the command we are executing, and any options that go with it
        self.command = command if command else 'check'

        self.options = options
        if self.options['version']:
            self.command = 'version'

        # make sure we have an actual command
        if not commands.allowed(self.command):
            raise ValueError("Unknown command %s" % self.command)

    def execute(self):

        commands.execute(self.command, self.options)
