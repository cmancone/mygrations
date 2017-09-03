from mygrations.core.parse.parser import parser
from mygrations.formats.mysql.definitions.column import column

class type_decimal( parser, column ):

    allowed_types = { 'real': True, 'double': True, 'float': True, 'decimal': True, 'numeric': True }

    decimals = ''
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
        { 'type': 'regexp', 'value': 'DEFAULT ([^\(\s\),]+)', 'optional': True, 'name': 'default' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self._errors = []
        self._warnings = []
        self._name = self._values['name'].strip( '`' )
        self._column_type = self._values['type']
        self.decimals = self._values['decimals']
        self._length = '%s.%s' % ( self._values['length'], self._values['decimals'] )
        self._unsigned = True if 'UNSIGNED' in self._values else False
        self._null = False if 'NOT NULL' in self._values else True
        self._default = self._values['default'] if 'default' in self._values else None

        # make sense of the default
        if self._default and len( self._default ) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip( "'" )
            self._warnings.append( 'Default value for numeric column %s does not need to be quoted' % self._name )
        elif self._default and self._default.lower() == 'null':
            self._default = None

        if self._default is None and not self._null:
            self._warnings.append( 'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' % ( self._name ) )

        # only a few types of field are allowed to have decimals
        if not self._column_type.lower() in self.allowed_types:
            self._errors.append( 'Column of type %s is not allowed to have a decimal length for column %s' % ( self._column_type, self._name ) )
