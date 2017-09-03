from mygrations.core.parse.parser import parser
from mygrations.formats.mysql.definitions.column import column

class type_enum( parser, column ):

    allowed_types = { 'set': True, 'enum': True }

    values = []
    has_comma = False

    # types enum( `young`,`middle`,`old` )
    rules = [
        { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'name' },
        { 'type': 'regexp', 'value': '\w+', 'name': 'type' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'delimited', 'name': 'values', 'quote': "'", 'separator': ',' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': 'NOT NULL', 'optional': True },
        { 'type': 'regexp', 'value': 'DEFAULT ([^\(\s\),]+)', 'optional': True, 'name': 'default' },
        { 'type': 'regexp', 'value': 'CHARACTER SET ([^\(\s\),]+)', 'name': 'character_set', 'optional': True },
        { 'type': 'regexp', 'value': 'COLLATE ([^\(\s\),]+)', 'name': 'collate', 'optional': True },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def __init__( self, rules = [] ):

        super().__init__( rules )

        self._errors = []
        self._warnings = []
        self.values = []

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self._name = self._values['name'].strip( '`' )
        self._column_type = self._values['type']
        self.values = self._values['values']
        self._length = self.values
        self._null = False if 'NOT NULL' in self._values else True
        self._default = self._values['default'] if 'default' in self._values else None
        self._character_set = self._values['character_set'] if 'character_set' in self._values else None
        self._collate = self._values['collate'] if 'collate' in self._values else None

        if self._character_set and len( self._character_set ) >= 2 and self._character_set[0] == "'" and self._character_set[-1] == "'":
            self._character_set = self._character_set.strip( "'" )

        if self._collate and len( self._collate ) >= 2 and self._collate[0] == "'" and self._collate[-1] == "'":
            self._collate = self._collate.strip( "'" )

        # make sense of the default
        if self._default and len( self._default ) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip( "'" )
        elif self._default:
            if self._default.lower() == 'null':
                self._default = None
            else:
                self._warnings.append( 'Default value of "%s" should have quotes for field %s' % (self._default,self._name) )

        if self._default and not( self._default in self.values ):
            self._errors.append( "Column %s has default value of %s but this is not an allowed value" % (self._name,self._default) )

        if self._default is None and not self._null:
            self._warnings.append( 'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' % ( self._name ) )

        # only a few types of field are allowed to use this
        if not self._column_type.lower() in self.allowed_types:
            self._errors.append( 'Column of type %s is not allowed to have a list of values for column %s' % ( self._column_type, self._name ) )
