from mygrations.core.parse.parser import parser

class type_character( parser ):

    allowed_collation_types = { 'char': True, 'varchar': True }

    # in this case we have much less disallowed than allowed
    disallowed_types = {
        'date':         True,
        'year':         True,
        'tinyblob':     True,
        'blob':         True,
        'mediumblob':   True,
        'longblob':     True,
        'tinytext':     True,
        'text':         True,
        'mediumtext':   True,
        'longtext':     True,
        'json':         True
    }

    definition_type = 'column'

    name = ''
    column_type = ''
    length = ''
    null = True
    default = ''
    character_set = ''
    collate = ''
    has_comma = False

    # name varchar(255) NOT NULL DEFAULT '' CHARACTER SET uf8 COLLATE utf8
    rules = [
        { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'name' },
        { 'type': 'regexp', 'value': '\w+', 'name': 'type' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'regexp', 'value': '\d+', 'name': 'length' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': 'NOT NULL', 'optional': True },
        { 'type': 'regexp', 'value': 'DEFAULT ([^\(\s\),]+)', 'optional': True, 'name': 'default' },
        { 'type': 'regexp', 'value': 'CHARACTER SET ([^\(\s\),]+)', 'name': 'character_set', 'optional': True },
        { 'type': 'regexp', 'value': 'COLLATE ([^\(\s\),]+)', 'name': 'collate', 'optional': True },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self.name = self._values['name'].strip( '`' )
        self.column_type = self._values['type']
        self.length = self._values['length']
        self.null = False if 'NOT NULL' in self._values else True
        self.default = self._values['default'] if 'default' in self._values else None
        self.character_set = self._values['character_set'] if 'character_set' in self._values else ''
        self.collate = self._values['collate'] if 'collate' in self._values else ''

        # make sense of the default
        if self.default and len( self.default ) >= 2 and self.default[0] == "'" and self.default[-1] == "'":
            self.default = self.default.strip( "'" )
        elif self.default:
            if self.default.lower() == 'null':
                self.default = None
            elif not self.default.isdigit():
                self.warnings.append( 'Default value of "%s" should have quotes for field %s' % (self.default,self.name) )

        if len( self.character_set ) >= 2 and self.character_set[0] == "'" and self.character_set[-1] == "'":
            self.character_set = self.character_set.strip( "'" )

        if len( self.collate ) >= 2 and self.collate[0] == "'" and self.collate[-1] == "'":
            self.collate = self.collate.strip( "'" )

        if self.character_set or self.collate:
            if not self.column_type.lower() in self.allowed_collation_types:
                self.errors.append( 'Column of type %s is not allowed to have a collation or character set for column %s' % ( self.column_type, self.name ) )

        if self.default is None and not self.null:
            self.warnings.append( 'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' % ( self.name ) )

        if self.column_type.lower() in self.disallowed_types:
            self.errors.append( 'Column of type %s is not allowed to have a length for column %s' % ( self.column_type, self.name ) )
