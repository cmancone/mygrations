from mygrations.core.parse.parser import parser

class type_enum( parser ):

    allowed_types = { 'set': True, 'enum': True }

    definition_type = 'column'

    name = ''
    column_type = ''
    values = []
    null = True
    default = ''
    character_set = ''
    collate = ''
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

        self.values = []

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self.name = self._values['name'].strip( '`' )
        self.column_type = self._values['type']
        self.values = self._values['values']
        self.null = False if 'NOT NULL' in self._values else True
        self.default = self._values['default'] if 'default' in self._values else None
        self.character_set = self._values['character_set'] if 'character_set' in self._values else ''
        self.collate = self._values['collate'] if 'collate' in self._values else ''

        if len( self.character_set ) >= 2 and self.character_set[0] == "'" and self.character_set[-1] == "'":
            self.character_set = self.character_set.strip( "'" )

        if len( self.collate ) >= 2 and self.collate[0] == "'" and self.collate[-1] == "'":
            self.collate = self.collate.strip( "'" )

        # make sense of the default
        if self.default and len( self.default ) >= 2 and self.default[0] == "'" and self.default[-1] == "'":
            self.default = self.default.strip( "'" )
        elif self.default:
            if self.default.lower() == 'null':
                self.default = None
            else:
                self.warnings.append( 'Default value of "%s" should have quotes for field %s' % (self.default,self.name) )

        if self.default and not( self.default in self.values ):
            self.errors.append( "Column %s has default value of %s but this is not an allowed value" % (self.name,self.default) )

        if self.default is None and not self.null:
            self.warnings.append( 'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' % ( self.name ) )

        # only a few types of field are allowed to use this
        if not self.column_type.lower() in self.allowed_types:
            self.errors.append( 'Column of type %s is not allowed to have a list of values for column %s' % ( self.column_type, self.name ) )
