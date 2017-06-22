from mygrations.core.parse.parser import parser

class index_unique( parser ):

    definition_type = 'unique'

    name = ''
    has_comma = False
    columns = []

    # UNIQUE account_id (account_id)
    rules = [
        { 'type': 'literal', 'value': 'UNIQUE' },
        { 'type': 'regexp', 'name': 'name', 'value': '[^\(]+' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'delimited', 'name': 'columns', 'separator': ',', 'quote': '`' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def __init__( self, rules = [] ):

        super().__init__( rules )

        self.columns = []

    process( self ):

        self.name = self._values['name']
        self.columns = self._values['columns']
        self.has_comma = True if 'ending_comma' in self._values else False
