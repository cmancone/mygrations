from mygrations.core.parse.parser import parser

class insert_values( parser ):

    # KEY account_id (account_id,name)
    rules = [
        { 'type': 'literal', 'value': '(' },
        { 'type': 'delimited', 'name': 'values', 'separator': ',', 'quote': "'" },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]
