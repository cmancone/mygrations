from mygrations.core.parse.parser import Parser
from .type import Type
class TypeText(Parser, Type):

    #***** Lint error if default is found for text field ******
    allowed_types = {
        'tinyblob': True,
        'blob': True,
        'mediumblob': True,
        'longblob': True,
        'tinytext': True,
        'text': True,
        'mediumtext': True,
        'longtext': True
    }

    has_comma = False

    # description text charset utf8 collate utf8
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
        self._length = ''
        self._has_default = 'default' in self._values
        self._default = self._values['default'] if 'default' in self._values else None
        self._column_type = self._values['type']
        self._null = False if 'NOT NULL' in self._values else True
        self._character_set = self._values['character_set'].strip("'") if 'character_set' in self._values else ''
        self._collate = self._values['collate'].strip("'") if 'collate' in self._values else ''

        # slightly more work on the default
        if self._default and len(self._default) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip("'")
        elif self._default:
            if self._default.lower() == 'null':
                self._default = None
            elif not self._default.isdigit():
                self._parsing_warnings.append(
                    'Default value of "%s" should have quotes for field %s' % (self._default, self._name)
                )
