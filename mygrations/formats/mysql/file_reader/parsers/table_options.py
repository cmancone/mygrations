from mygrations.core.parse.parser import parser

class table_options( parser ):

    name = ''
    value = ''

    # UNIQUE account_id (account_id)
    rules = [
        { 'type': 'regexp', 'value': '[^=]{1,30}', 'name': 'name' },
        { 'type': 'literal', 'value': '=' },
        { 'type': 'regexp', 'value': '[^\s;]+', 'name': 'value' }
    ]

    def process( self ):

        self.name = self._values['name'].strip()
        self.value = self._values['value'].strip()
