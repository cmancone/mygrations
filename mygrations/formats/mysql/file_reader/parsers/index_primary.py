from mygrations.core.parse.parser import parser

class index_primary( parser ):

    # PRIMARY KEY (`id`),
    rules = [ { 'type': 'literal', 'value': 'PRIMARY KEY' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'name': 'field', 'value': '[^\)]+' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' } ]
