#!/usr/bin/env python3

import argparse
from mygrations.mygrate import mygrate

# argument parsing
parser = argparse.ArgumentParser()
parser.add_argument(
    'command',
    nargs='?',
    default='version',
    choices=['version', 'apply', 'check', 'import', 'plan', 'plan_export'],
    help='Action to execute (default: version)'
)
parser.add_argument('--env', default='.env', help='Location of environment file (default: .env)')
parser.add_argument(
    '--config', default='mygrate.conf', help='Location of mygrate configuration file (default: mygrate.conf)'
)
parser.add_argument('-f', dest='force', action='store_true', help='Ignore errors/warnings and execute command anyway')
parser.add_argument('-v', dest='version', action='store_true', help='Display version')
args = parser.parse_args()

# load up a mygrate object
my = mygrate(args.command, vars(args))

# and execute
my.execute()
