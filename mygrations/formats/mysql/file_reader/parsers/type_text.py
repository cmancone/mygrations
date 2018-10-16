from mygrations.core.parse.parser import parser
from mygrations.formats.mysql.definitions.column import column
class type_text(parser, column):

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

        self._errors = []
        self._warnings = []
        self._name = self._values['name'].strip('`')
        self._length = ''
        self._default = None
        self._column_type = self._values['type']
        self._null = False if 'NOT NULL' in self._values else True
        self._character_set = self._values['character_set'].strip("'") if 'character_set' in self._values else ''
        self._collate = self._values['collate'].strip("'") if 'collate' in self._values else ''

        if self._column_type.lower() == 'datetime':
            pass
        elif not self._column_type.lower() in self.allowed_types:
            self._errors.append('Column of type %s must have a length for column %s' % (self._column_type, self._name))
        elif 'default' in self._values:
            self._errors.append(
                'Column of type %s is not allowed to have a default value for column %s' %
                (self._column_type, self._name)
            )
