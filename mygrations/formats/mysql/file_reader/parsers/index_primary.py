from mygrations.core.parse.parser import parser

class index_primary( parser ):

    definition_type = 'primary'

    column = ''
    has_comma = False
    name = ''

    # PRIMARY KEY (`id`),
    rules = [
        { 'type': 'literal', 'value': 'PRIMARY KEY' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'regexp', 'name': 'column', 'value': '[^\)]+' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def process( self ):

        self.column = self._values['column'].strip().strip( '`' )
        self.has_comma = True if 'ending_comma' in self._values else False
        self.name = self.column
