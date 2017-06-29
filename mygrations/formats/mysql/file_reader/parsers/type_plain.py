from mygrations.core.parse.parser import parser

class type_plain( parser ):

    definition_type = 'column'

    name = ''
    column_type = ''
    default = ''
    has_comma = False

    # created date
    rules = [
        { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'name' },
        { 'type': 'regexp', 'value': '\w+', 'name': 'type' },
        { 'type': 'regexp', 'value': 'DEFAULT [^\(\s\)]+', 'optional': True, 'name': 'default' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self.name = self._values['name']
        self.column_type = self._values['type']
        self.default = self._values['default'] if 'default' in self._values else ''
