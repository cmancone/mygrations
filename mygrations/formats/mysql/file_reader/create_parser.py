from mygrations.core.parse.parser import parser

from .parsers import *

class create_parser( parser ):

    semicolon = False
    name = ''
    definitions = []
    table_options = []

    def __init__( self, rules = [] ):

        self.definitions = []
        self.table_options = []

    # this defines the rules for the parsing engine.  Yes, I decided to try to build
    # a parsing engine to parse the MySQL.  Seems like a reasonable choice at the
    # moment, but we'll see how it works out in the long run.  The setup you see here
    # is a compromise between the declarative programming principles I like and the
    # time it takes to actually build such a system, especially for a relatively
    # limited use-case.  In the long run if this works well it could probably
    # become its own multi-purpose tool.  These "rules" basically boil down to:
    #
    # CREATE TABLE table_name ( [definitions] ) [options];
    #
    # definitions and options have their own patterns of allowed values and rules,
    # which also have to be defined.  That is handled below for the sake of brevity
    rules = [
        { 'type': 'literal', 'value': 'CREATE TABLE' },
        { 'type': 'regexp', 'value': '\S+', 'name': 'name' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'children', 'name': 'definitions', 'classes': [
            index_primary, index_key, index_unique, constraint_foreign, type_character, type_numeric, type_decimal, type_text, type_enum, type_plain
        ] },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'children', 'name': 'table_options', 'classes': [ table_options ], 'optional': True },
        { 'type': 'literal', 'value': ';', 'optional': True, 'name': 'closing_semicolon' }
    ]

    def process( self ):

        self.semicolon = True if 'closing_semicolon' in self._values else False
        self.name = self._values['name'].strip( '`' )
        self.definitions = self._values['definitions']
        self.table_options = self._values['table_options']

        ncols = 0
        for definition in self.definitions:
            if definition.definition_type == 'column':
                ncols += 1

        if not self.name:
            self.errors.append( 'Table name is required' )

        if not ncols:
            self.errors.append( "Table %s has no columns" % self.name )
