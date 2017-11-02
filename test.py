#!/usr/bin/python3
import unittest

import sys, os
sys.path.append( os.path.dirname( os.path.realpath( __file__ ) ) )

glob = 'test*.py'
if len( sys.argv ) > 1:
    path = sys.argv[1]
    # generally expecting a directory.  If it is a file then find the parent directory
    if os.path.isfile( path ):
        glob = os.path.basename( path )
        path = os.path.dirname( path )
    elif not os.path.isdir( path ):
        raise ValueError( "Cannot find file or directory named %s" % path )

    # convert to python speak
    path = path.replace( '/', '.' ).strip( '.' )
else:
    path = 'tests'

tests = unittest.TestLoader().discover( path, pattern=glob )
testRunner = unittest.runner.TextTestRunner()
testRunner.run(tests)
