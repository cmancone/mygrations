from mygrations.core.parse.parser import parser

class type_numeric( parser ):

    allowed_types = {
        'bit':          True,
        'tinyint':      True,
        'smallint':     True,
        'mediumint':    True,
        'int':          True,
        'integer':      True,
        'bigint':       True,
        'decimal':      True,
        'numeric':      True,
        'char':         True,
        'varchar':      True
    }

    definition_type = 'column'

    name = ''
    column_type = ''
    length = ''
    unsigned = False
    null = True
    default = ''
    auto_increment = False
    has_comma = False
    is_char = False

    # `created` int(10) unsigned not null default 0 AUTO_INCREMENT
    rules = [
        { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'name' },
        { 'type': 'regexp', 'value': '\w+', 'name': 'type' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'regexp', 'value': '\d+', 'name': 'length' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': 'UNSIGNED', 'optional': True },
        { 'type': 'literal', 'value': 'NOT NULL', 'optional': True },
        { 'type': 'regexp', 'value': 'DEFAULT ([^\(\s\),]+)', 'name': 'default', 'optional': True },
        { 'type': 'literal', 'value': 'AUTO_INCREMENT', 'optional': True },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self.name = self._values['name']
        self.column_type = self._values['type']
        self.length = self._values['length']
        self.unsigned = True if 'UNSIGNED' in self._values else False
        self.null = False if 'NOT NULL' in self._values else True
        self.default = self._values['default'] if 'default' in self._values else None
        self.auto_increment = True if 'AUTO_INCREMENT' in self._values else False
        self.is_char = self.column_type in [ 'char', 'varchar' ]

        # double check unsigned
        if self.unsigned and self.is_char:
            self.errors.append( "Column %s is a character type and cannot be unsigned" % self.name )

        # make sense of the default
        if self.default and len( self.default ) >= 2 and self.default[0] == "'" and self.default[-1] == "'":
            self.default = self.default.strip( "'" )
            if not self.is_char:
                self.warnings.append( 'Default value for numeric column %s does not need to be quoted' % self.name )
        elif self.default:
            if self.default.lower() == 'null':
                self.default = None
            elif self.is_char:
                self.warnings.append( 'Default value for column %s should be quoted' % self.name )

        if self.default is None and not self.null and not self.auto_increment:
            self.warnings.append( 'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' % ( self.name ) )

        if self.auto_increment and self.is_char:
            self.errors.append( 'Column %s is an auto increment character field: only numeric fields can auto increment' % ( self.name ) )

        # only a few types of field are allowed to have decimals
        if not self.column_type.lower() in self.allowed_types:
            self.errors.append( 'Column of type %s is not allowed to have a length for column %s' % ( self.column_type, self.name ) )
