from mygrations.core.parse.parser import parser

class table_options( parser ):

    # UNIQUE account_id (account_id)
    rules = [
        { 'type': 'regexp', 'value': '[^=]{1,25}', 'name': 'option' },
        { 'type': 'literal', 'value': '=' },
        { 'type': 'regexp', 'value': '[^\s;]+', 'name': 'value' }
    ]
