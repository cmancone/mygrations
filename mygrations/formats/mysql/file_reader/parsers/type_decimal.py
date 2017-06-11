from mygrations.core.parse.parser import parser

class type_decimal( parser ):

    # longitude float(20,4) unsigned default null
    rules = [ { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'value': '\d+', 'name': 'length' }, { 'type': 'literal', 'value': ',', 'name': 'separating_comma' }, { 'type': 'regexp', 'value': '\d+', 'name': 'decimals' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': 'unsigned', 'optional': True }, { 'type': 'literal', 'value': 'not null', 'optional': True }, { 'type': 'regexp', 'value': 'default [^\(\s\)]+', 'optional': True, 'name': 'default' }, { 'type': 'literal', 'value': 'auto_increment', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' } ]
