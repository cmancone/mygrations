from mygrations.core.parse import parser

from .type_numeric import type_numeric
from .type_decimal import type_decimal
from .type_character import type_character
from .type_plain import type_plain
from .type_text import type_text
from .index_primary import index_primary
from .index_key import index_key
from .index_unique import index_unique
from .constraint_foreign import constraint_foreign

class create_parser( parser ):

    string = ''

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
        { 'type': 'regexp', 'value': '\S+', 'name': 'table' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'children', 'name': 'definitions' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'values', 'name': 'table_options', 'optional': True },
        { 'type': 'literal', 'value': ';', 'optional': True }
        ### don't forget type of delimited, which is used in children
    ]

    ###### A line can potentially match multiple elements.  Imagine a mistake like this:
    # varchar(255) UNSIGNED NOT NULL DEFAULT '' CHARACTER SET 'utf8'
    # It is a syntax error and should be identified as such

    ###### Track match percentage to get syntax errors

    # I might have to find another way to organize this in the long run.  Likely
    # split each of these out to its own class with its own definition.
    # for the moment though this will work
    child_rules = {
        'definitions': [

            # `created` int(10) unsigned not null default 0 AUTO_INCREMENT
            [ { 'type': 'regexp', 'value': '\S+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'value': '\d+', 'name': 'length' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': 'unsigned', 'optional': True }, { 'type': 'literal', 'value': 'not null', 'optional': True }, { 'type': 'regexp', 'value': 'default \S+', 'name': 'default', 'optional': True }, { 'type': 'literal', 'value': 'auto_increment', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # longitude float(20,4) unsigned default null
            [ { 'type': 'regexp', 'value': '\S+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'value': '\d+', 'name': 'length' }, { 'type': 'literal', 'value': ',' }, { 'type': 'regexp', 'value': '\d+', 'name': 'decimals' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': 'unsigned', 'optional': True }, { 'type': 'literal', 'value': 'not null', 'optional': True }, { 'type': 'regexp', 'value': 'default \S+', 'optional': True }, { 'type': 'literal', 'value': 'auto_increment', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # created date
            [ { 'type': 'regexp', 'value': '\S+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # name varchar(255) NOT NULL DEFAULT '' CHARACTER SET uf8 COLLATE utf8
            [ { 'type': 'regexp', 'value': '\S+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'value': '\d+', 'name': 'length' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': 'not null', 'optional': True }, { 'type': 'regexp', 'value': 'default \S+', 'optional': True }, { 'type': 'regexp', 'value': 'CHARACTER SET \S+', 'name': 'characterset', 'optional': True }, { 'type': 'regexp', 'value': 'COLLATE \S+', 'name': 'collate', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # description text charset utf8 collate utf8
            [ { 'type': 'regexp', 'value': '\S+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': 'not null', 'optional': True }, { 'type': 'regexp', 'value': 'CHARACTER SET \S+', 'name': 'characterset', 'optional': True }, { 'type': 'regexp', 'value': 'COLLATE \S+', 'name': 'collate', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # types SET( `young`,`middle`,`old` )
            [ { 'type': 'regexp', 'value': '\S+', 'name': 'field' }, { 'type': 'literal', 'value': 'set' }, { 'type': 'literal', 'value': '(' }, { 'type': 'delimited', 'name': 'values', 'quote': "'", 'separator': ',' }, { 'type': 'literal', 'value': ')' }, { 'type': 'regexp', 'value': 'default \S+', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # types enum( `young`,`middle`,`old` )
            [ { 'type': 'regexp', 'value': '\S+', 'name': 'field' }, { 'type': 'literal', 'value': 'enum' }, { 'type': 'literal', 'value': '(' }, { 'type': 'delimited', 'name': 'values', 'quote': "'", 'separator': ',' }, { 'type': 'literal', 'value': ')' }, { 'type': 'regexp', 'value': 'default \S+', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # PRIMARY KEY (`id`),
            [ { 'type': 'literal', 'value': 'PRIMARY KEY' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'name': 'field', 'value': '\S+' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # KEY account_id (account_id,name)
            [ { 'type': 'literal', 'value': 'KEY' }, { 'type': 'regexp', 'name': 'key_name', 'value': '\S+' }, { 'type': 'literal', 'value': '(' }, { 'type': 'delimited', 'name': 'fields', 'separator': ',' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # UNIQUE account_id (account_id)
            [ { 'type': 'literal', 'value': 'UNIQUE' }, { 'type': 'regexp', 'name': 'key_name', 'value': '\S+' }, { 'type': 'literal', 'value': '(' }, { 'type': 'delimited', 'name': 'fields', 'separator': ',' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': ',', 'optional': True } ],

            # CONSTRAINT `accounts_status_id_ref_account_statuses_id` FOREIGN KEY (`status_id`) REFERENCES `account_statuses` (`id`) ON UPDATE CASCADE
            [ { 'type': 'literal', 'value': 'CONSTRAINT' }, { 'type': 'regexp', 'name': 'constraint_name', 'value': '\S+' }, { 'type': 'literal', 'value': 'FOREIGN KEY (' }, { 'type': 'regexp', 'name': 'field_name', 'value': '\S+' }, { 'type': 'literal', 'value': ') REFERENCES' }, { 'type': 'regexp', 'name': 'foreign_table', 'value': '\S+' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'name': 'foreign_field', 'value': '\S+' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': 'ON DELETE CASCADE', 'optional': True }, { 'type': 'literal', 'value': 'ON DELETE NO ACTION', 'optional': True }, { 'type': 'literal', 'value': 'ON DELETE RESTRICT', 'optional': True }, { 'type': 'literal', 'value': 'ON DELETE SET DEFAULT', 'optional': True }, { 'type': 'literal', 'value': 'ON DELETE SET NULL', 'optional': True }, { 'type': 'literal', 'value': 'ON UPDATE CASCADE', 'optional': True }, { 'type': 'literal', 'value': 'ON UPDATE NO ACTION', 'optional': True }, { 'type': 'literal', 'value': 'ON UPDATE RESTRICT', 'optional': True }, { 'type': 'literal', 'value': 'ON UPDATE SET DEFAULT', 'optional': True }, { 'type': 'literal', 'value': 'ON UPDATE SET NULL', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True } ]
        ]
    }

    def __init__( self, string ):

        self.string = string;

    def parse( self ):

        print( 'create!' )
        return ''
