from mygrations.core.parse.parser import parser

class type_enum( parser ):

    #*********** Also covers SET ********

    # types enum( `young`,`middle`,`old` )
    rules = [ { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'field_type' }, { 'type': 'literal', 'value': '(' }, { 'type': 'delimited', 'name': 'values', 'quote': "'", 'separator': ',' }, { 'type': 'literal', 'value': ')' }, { 'type': 'regexp', 'value': 'default [^\(\s\)]+', 'optional': True, 'name': 'default' }, { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' } ]

