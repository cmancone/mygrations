from mygrations.core.parse.parser import parser

class index_key( parser ):

    definition_type = 'index'

    name = ''
    has_comma = False
    columns = []

    # KEY account_id (account_id,name)
    rules = [
        { 'type': 'literal', 'value': 'KEY' },
        { 'type': 'regexp', 'name': 'name', 'value': '[^\(\s\)]+' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'delimited', 'name': 'columns', 'separator': ',', 'quote': '`' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def __init__( self, rules = [] ):

        super().__init__( rules )

        self.columns = []

    def process( self ):

        self.name = self._values['name']
        self.columns = self._values['columns']
        self.has_comma = True if 'ending_comma' in self._values else False
