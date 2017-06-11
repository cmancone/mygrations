from mygrations.core.parse.parser import parser

class index_unique( parser ):

    # UNIQUE account_id (account_id)
    rules = [ { 'type': 'literal', 'value': 'UNIQUE' }, { 'type': 'regexp', 'name': 'key_name', 'value': '[^\(]+' }, { 'type': 'literal', 'value': '(' }, { 'type': 'delimited', 'name': 'fields', 'separator': ',', 'quote': '`' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' } ]
