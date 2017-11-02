from collections import OrderedDict

from mygrations.core.parse.parser import parser
from mygrations.formats.mysql.definitions.constraint import constraint
from mygrations.formats.mysql.definitions.index import index
from mygrations.formats.mysql.definitions.column import column
from mygrations.formats.mysql.definitions.table import table

from .parsers import *

class create_parser( parser, table ):

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
        { 'type': 'children', 'name': 'table_options', 'classes': [ table_option ], 'optional': True },
        { 'type': 'literal', 'value': ';', 'optional': True, 'name': 'closing_semicolon' }
    ]

    def process( self ):

        self.semicolon = True if 'closing_semicolon' in self._values else False
        self._name = self._values['name'].strip( '`' )
        self._definitions = self._values['definitions']
        self._options = self._values['table_options'] if 'table_options' in self._values else []
        self._columns = OrderedDict()
        self._indexes = OrderedDict()
        self._constraints = OrderedDict()
        self._errors = []
        self._warnings = []
        self._primary = ''

        # ignore the AUTO_INCREMENT option: there is no reason for us to ever manage that
        self._options = [ opt for opt in self._options if opt.name != 'AUTO_INCREMENT' ]

        for definition in self._definitions:
            if isinstance( definition, column ):
                self._columns[definition.name] = definition
            elif isinstance( definition, index ):
                self._indexes[definition.name] = definition

                if definition.index_type == 'PRIMARY':
                    if self._primary:
                        self._errors.append( 'Found more than one primary column for table %s' % ( self._name ) )
                    else:
                        self._primary = definition
            elif isinstance( definition, constraint ):
                self._constraints[definition.name] = definition

            if definition.errors:
                for error in definition.errors:
                    self._errors.append( '%s in table %s' % ( error, self._name ) )

            if definition.warnings:
                for warning in definition.warnings:
                    self._warnings.append( '%s in table %s' % ( warning, self._name ) )

        if not self._name:
            self._errors.append( 'Table name is required' )

        if not len( self._columns ):
            self._errors.append( "Table %s has no columns" % self._name )

        if not self.semicolon:
            self._errors.append( "Missing ending semicolon for table %s" % self._name )
