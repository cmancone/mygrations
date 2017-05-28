#!/usr/bin/python3

import argparse
from mygrations.mygrate import mygrate

# argument parsing
parser = argparse.ArgumentParser()
parser.add_argument( 'command', nargs='?', default='import', choices=[ 'import' ], help='Action to execute (default: import)' )
parser.add_argument( '--env', dest='env', default='.env', help='Location of environment file (default: .env)' )
args = parser.parse_args()

# load up a mygrate object
my = mygrate( args.command, vars( args ) )

# and execute
my.execute()
