__ver__ = '0.1'

from .core import commands

class mygrate( object ):

    command = ''
    options = {}

    def __init__( self, command, options = {} ):

        # store the name of the command we are executing, and any options that go with it
        self.command = command if command else 'import'

        self.options = options

        # make sure we have an actual command
        if not commands.allowed( self.command ):
            raise ValueError( "Unknown command %s" % self.command )

    def execute( self ):

        commands.execute( self.command, self.options )
