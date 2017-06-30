from mygrations.core.parse.parser import parser

class type_text( parser ):

    #***** Lint error if default is found for text field ******
    allowed_types = {
        'tinyblob':     True,
        'blob':         True,
        'mediumblob':   True,
        'longblob':     True,
        'tinytext':     True,
        'text':         True,
        'mediumtext':   True,
        'longtext':     True
    }

    definition_type = 'column'

    name = ''
    column_type = ''
    length = ''
    unsigned = False
    null = True
    auto_increment = False
    has_comma = False

    # description text charset utf8 collate utf8
    rules = [
        { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'name' },
        { 'type': 'regexp', 'value': '\w+', 'name': 'type' },
        { 'type': 'literal', 'value': 'NOT NULL', 'optional': True },
        { 'type': 'regexp', 'value': 'DEFAULT [^\(\s\)]+', 'optional': True, 'name': 'default' },
        { 'type': 'regexp', 'value': 'CHARACTER SET [^\(\s\)]+', 'name': 'characterset', 'optional': True },
        { 'type': 'regexp', 'value': 'COLLATE [^\(\s\)]+', 'name': 'collate', 'optional': True },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self.name = self._values['name']
        self.column_type = self._values['type']
        self.null = False if 'NOT NULL' in self._values else True
        self.character_set = self._values['character_set'] if 'character_set' in self._values else ''
        self.collate = self._values['collate'] if 'collate' in self._values else ''

        if 'default' in self._values:
            self.errors.append( 'Column of type %s is not allowed to have a default value for column %s' % ( self.column_type, self.name ) )

        if not self.column_type.lower() in self.allowed_types:
            self.errors.append( 'Column of type %s must have a length for column %s' % ( self.column_type, self.name ) )
