from mygrations.core.parse.parser import Parser
from mygrations.formats.mysql.definitions.column import Column
class TypePlain(Parser, Column):

    has_comma = False

    # created date
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
        'value': 'NOT NULL',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'DEFAULT ([^\(\s\),]+)',
        'optional': True,
        'name': 'default'
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
        self._column_type = self._values['type']
        self._default = self._values['default'].strip("'") if 'default' in self._values else None
        self._null = False if 'NOT NULL' in self._values else True

        # make sense of the default
        if self._default and self._default.lower() == 'null':
            self._default = None

        if self._default is None and not self._null:
            self._warnings.append(
                'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' %
                (self._name)
            )
