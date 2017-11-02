#!/usr/bin/python3

import argparse
from mygrations.mygrate import mygrate

# argument parsing
parser = argparse.ArgumentParser()
parser.add_argument( 'command', nargs='?', default='check', choices=[ 'check', 'import', 'plan', 'plan_export' ], help='Action to execute (default: check)' )
parser.add_argument( '--env', default='.env', help='Location of environment file (default: .env)' )
parser.add_argument( '--config', default='mygrate.conf', help='Location of mygrate configuration file (default: mygrate.conf)' )
args = parser.parse_args()

# load up a mygrate object
my = mygrate( args.command, vars( args ) )

# and execute
my.execute()
