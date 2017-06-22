from mygrations.core.parse.parser import parser

class insert_values( parser ):

    has_comma = False
    values = []

    rules = [
        { 'type': 'literal', 'value': '(' },
        { 'type': 'delimited', 'name': 'values', 'separator': ',', 'quote': "'" },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def __init__( self, rules = [] ):

        super().__init__( rules )

        self.values = []

    process( self ):

        self.values = self._values['values']
        self.has_comma = True if 'ending_comma' in self._values else False
