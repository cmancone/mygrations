from mygrations.core.parse.parser import parser

class type_decimal( parser ):

    allowed_types = { 'real': True, 'double': True, 'float': True, 'decimal': True, 'numeric': True }

    definition_type = 'column'

    name = ''
    column_type = ''
    length = ''
    decimals = ''
    unsigned = False
    null = True
    default = ''
    has_comma = False

    # longitude float(20,4) unsigned default null
    rules = [
        { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'name' },
        { 'type': 'regexp', 'value': '\w+', 'name': 'type' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'regexp', 'value': '\d+', 'name': 'length' },
        { 'type': 'literal', 'value': ',', 'name': 'separating_comma' },
        { 'type': 'regexp', 'value': '\d+', 'name': 'decimals' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': 'UNSIGNED', 'optional': True },
        { 'type': 'literal', 'value': 'NOT NULL', 'optional': True },
        { 'type': 'regexp', 'value': 'DEFAULT [^\(\s\)]+', 'optional': True, 'name': 'default' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self.name = self._values['name']
        self.column_type = self._values['type']
        self.length = self._values['length']
        self.decimals = self._values['decimals']
        self.unsigned = True if 'UNSIGNED' in self._values else False
        self.null = False if 'NOT NULL' in self._values else True
        self.default = self._values['default'] if 'default' in self._values else ''

        if !self.null and self.default.lower() == 'null':
            self.errors.append( 'Default set to null for column %s but column is not nullable' % self.name )

        # only a few types of field are allowed to have decimals
        if not self.column_type.lower() in self.allowed_types:
            self.errors.append( 'Column of type %s is not allowed to have a decimal length for column %s' % ( self.column_type, self.name ) )
