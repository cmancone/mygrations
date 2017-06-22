from mygrations.core.parse.parser import parser

class type_character( parser ):

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
        { 'type': 'regexp', 'value': 'default [^\(\s\)]+', 'optional': True, 'name': 'default' },
        { 'type': 'regexp', 'value': 'CHARACTER SET [^\(\s\)]+', 'name': 'character_set', 'optional': True },
        { 'type': 'regexp', 'value': 'COLLATE [^\(\s\)]+', 'name': 'collate', 'optional': True },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    process( self ):

        self.has_comma = True if 'ending_comma' in self._values else False

        self.name = self._values['name']
        self.column_type = self._values['type']
        self.length = self._values['length']
        self.null = False if 'NOT NULL' in self._values else True
        self.default = self._values['default'] if 'default' in self._values else ''
        self.character_set = self._values['character_set'] if 'character_set' in self._values else ''
        self.collate = self._values['collate'] if 'collate' in self._values else ''

        if !self.null and self.default.lower() == 'null':
            self.errors.append( 'Default set to null for column %s but column is not nullable' % self.name )
