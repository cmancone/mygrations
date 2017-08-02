from mygrations.core.parse.parser import parser
from mygrations.formats.mysql.definitions.column import column

class type_character( parser, column ):

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

        self._name = self._values['name'].strip( '`' )
        self._column_type = self._values['type']
        self._length = self._values['length']
        self._null = False if 'NOT NULL' in self._values else True
        self._default = self._values['default'] if 'default' in self._values else None
        self.character_set = self._values['character_set'] if 'character_set' in self._values else ''
        self.collate = self._values['collate'] if 'collate' in self._values else ''

        # make sense of the default
        if self._default and len( self._default ) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip( "'" )
        elif self._default:
            if self._default.lower() == 'null':
                self._default = None
            elif not self._default.isdigit():
                self.warnings.append( 'Default value of "%s" should have quotes for field %s' % (self._default,self._name) )

        if len( self.character_set ) >= 2 and self.character_set[0] == "'" and self.character_set[-1] == "'":
            self.character_set = self.character_set.strip( "'" )

        if len( self.collate ) >= 2 and self.collate[0] == "'" and self.collate[-1] == "'":
            self.collate = self.collate.strip( "'" )

        if self.character_set or self.collate:
            if not self._column_type.lower() in self.allowed_collation_types:
                self.errors.append( 'Column of type %s is not allowed to have a collation or character set for column %s' % ( self._column_type, self._name ) )

        if self._default is None and not self._null:
            self.warnings.append( 'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' % ( self._name ) )

        if self._column_type.lower() in self.disallowed_types:
            self.errors.append( 'Column of type %s is not allowed to have a length for column %s' % ( self._column_type, self._name ) )

        self._attributes = {}
        if self.character_set:
            self._attributes['CHARACTER SET'] = self.character_set
        if self.collate:
            self._attributes['COLLATE'] = self.collate
