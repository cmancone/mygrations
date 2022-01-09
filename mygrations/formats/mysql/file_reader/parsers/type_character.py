from mygrations.core.parse.parser import Parser
from .type import Type
class TypeCharacter(Parser, Type):

    allowed_collation_types = {'char': True, 'varchar': True}

    # in this case we have much less disallowed than allowed
    disallowed_types = {
        'date': True,
        'year': True,
        'tinyblob': True,
        'blob': True,
        'mediumblob': True,
        'longblob': True,
        'tinytext': True,
        'text': True,
        'mediumtext': True,
        'longtext': True,
        'json': True
    }

    has_comma = False

    # name varchar(255) NOT NULL DEFAULT '' CHARACTER SET uf8 COLLATE utf8
    # hackish? maybe (i.e. yes) the repeated COLLATE and CHARACTER SETS take care of uncertain
    # ordering.  I could also use `children` which is order-agnostic, but I'm being lazy
    rules = [{
        'type': 'regexp',
        'value': '[^\(\s\)]+',
        'name': 'name'
    }, {
        'type': 'regexp',
        'value': '\w+',
        'name': 'type'
    }, {
        'type': 'literal',
        'value': '('
    }, {
        'type': 'regexp',
        'value': '\d+',
        'name': 'length'
    }, {
        'type': 'literal',
        'value': ')'
    }, {
        'type': 'regexp',
        'value': 'COLLATE ([^\(\s\),]+)',
        'name': 'collate',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'CHARACTER SET ([^\(\s\),]+)',
        'name': 'character_set',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'COLLATE ([^\(\s\),]+)',
        'name': 'collate',
        'optional': True
    }, {
        'type': 'literal',
        'value': 'NOT NULL',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'COLLATE ([^\(\s\),]+)',
        'name': 'collate',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'CHARACTER SET ([^\(\s\),]+)',
        'name': 'character_set',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'COLLATE ([^\(\s\),]+)',
        'name': 'collate',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'DEFAULT ([^\(\s\),]+)',
        'optional': True,
        'name': 'default'
    }, {
        'type': 'regexp',
        'value': 'COLLATE ([^\(\s\),]+)',
        'name': 'collate',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'CHARACTER SET ([^\(\s\),]+)',
        'name': 'character_set',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'COLLATE ([^\(\s\),]+)',
        'name': 'collate',
        'optional': True
    }, {
        'type': 'literal',
        'value': ',',
        'optional': True,
        'name': 'ending_comma'
    }]

    def process(self):

        self.has_comma = True if 'ending_comma' in self._values else False

        self._parsing_errors = []
        self._parsing_warnings = []
        self._schema_errors = []
        self._schema_warnings = []
        self._name = self._values['name'].strip('`')
        self._column_type = self._values['type']
        self._length = self._values['length']
        self._null = False if 'NOT NULL' in self._values else True
        self._has_default = 'default' in self._values
        self._default = self._values['default'] if 'default' in self._values else None
        self._character_set = self._values['character_set'] if 'character_set' in self._values else None
        self._collate = self._values['collate'] if 'collate' in self._values else None

        # make sense of the default
        if self._default and len(self._default) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip("'")
        elif self._default:
            if self._default.lower() == 'null':
                self._default = None
            elif not self._default.isdigit():
                self._parsing_warnings.append(
                    'Default value of "%s" should have quotes for field %s' % (self._default, self._name)
                )

        if self._character_set and len(self._character_set
                                       ) >= 2 and self._character_set[0] == "'" and self._character_set[-1] == "'":
            self._character_set = self._character_set.strip("'")

        if self._collate and len(self._collate) >= 2 and self._collate[0] == "'" and self._collate[-1] == "'":
            self._collate = self._collate.strip("'")

        self._attributes = {}
        if self._character_set:
            self._attributes['CHARACTER SET'] = self._character_set
        if self._collate:
            self._attributes['COLLATE'] = self._collate
