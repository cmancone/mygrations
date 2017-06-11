from mygrations.core.parse.parser import parser

class type_plain( parser ):

    # created date
    rules = [ { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'regexp', 'value': 'default [^\(\s\)]+', 'optional': True, 'name': 'default' }, { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' } ]
