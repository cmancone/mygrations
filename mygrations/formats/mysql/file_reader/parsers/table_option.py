from mygrations.core.parse.parser import parser

class table_option( parser ):

    name = ''
    value = ''

    # UNIQUE account_id (account_id)
    rules = [
        { 'type': 'regexp', 'value': '[^=]{1,30}', 'name': 'name' },
        { 'type': 'literal', 'value': '=' },
        { 'type': 'regexp', 'value': '[^\s;]+', 'name': 'value' }
    ]

    def process( self ):

        self._errors = []
        self._warnings = []
        self.name = self._values['name'].strip()
        self.value = self._values['value'].strip()
