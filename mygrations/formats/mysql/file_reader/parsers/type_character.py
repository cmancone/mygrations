from mygrations.core.parse.parser import parser

class type_character( parser ):

    # name varchar(255) NOT NULL DEFAULT '' CHARACTER SET uf8 COLLATE utf8
    rules = [ { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'value': '\d+', 'name': 'length' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': 'not null', 'optional': True }, { 'type': 'regexp', 'value': 'default [^\(\s\)]+', 'optional': True, 'name': 'default' }, { 'type': 'regexp', 'value': 'CHARACTER SET [^\(\s\)]+', 'name': 'characterset', 'optional': True }, { 'type': 'regexp', 'value': 'COLLATE [^\(\s\)]+', 'name': 'collate', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' } ]
