from .base import base
import mygrations

def execute( options ):

    obj = version( options )
    obj.execute()

class version( base ):

    def execute( self ):
        print( 'mygrations v%s' % mygrations.__version__ )
        print( 'Copyright (c) 2017 Conor Mancone (cmancone@gmail.com)' )
        print( 'MIT License' )
