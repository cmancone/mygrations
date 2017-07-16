from mygrations.core.parse.parser import parser

class type_plain( parser ):

    definition_type = 'column'

    name = ''
    column_type = ''
    default = ''
    has_comma = False
    null = False

    # created date
    rules = [
        { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'name' },
        { 'type': 'regexp', 'value': '\w+', 'name': 'type' },
        { 'type': 'literal', 'value': 'NOT NULL', 'optional': True },
        { 'type': 'regexp', 'value': 'DEFAULT ([^\(\s\),]+)', 'optional': True, 'name': 'default' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self.name = self._values['name']
        self.column_type = self._values['type']
        self.default = self._values['default'].strip( "'" ) if 'default' in self._values else None
        self.null = False if 'NOT NULL' in self._values else True

        # make sense of the default
        if self.default and self.default.lower() == 'null':
            self.default = None

        if self.default is None and not self.null:
            self.warnings.append( 'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' % ( self.name ) )
