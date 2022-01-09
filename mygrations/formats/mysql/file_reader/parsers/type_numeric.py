from mygrations.core.parse.parser import Parser
from .type import Type
class TypeNumeric(Parser, Type):

    allowed_types = {
        'bit': True,
        'tinyint': True,
        'smallint': True,
        'mediumint': True,
        'int': True,
        'integer': True,
        'bigint': True,
        'decimal': True,
        'numeric': True,
        'char': True,
        'varchar': True
    }

    has_comma = False
    is_char = False

    # `created` int(10) unsigned not null default 0 AUTO_INCREMENT
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
        'type': 'literal',
        'value': 'UNSIGNED',
        'optional': True
    }, {
        'type': 'literal',
        'value': 'NOT NULL',
        'optional': True
    }, {
        'type': 'regexp',
        'value': 'DEFAULT ([^\(\s\),]+)',
        'name': 'default',
        'optional': True
    }, {
        'type': 'literal',
        'value': 'AUTO_INCREMENT',
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
        self._unsigned = True if 'UNSIGNED' in self._values else False
        self._null = False if 'NOT NULL' in self._values else True
        self._has_default = 'default' in self._values
        self._default = self._values['default'] if 'default' in self._values else None
        self._auto_increment = True if 'AUTO_INCREMENT' in self._values else False
        self.is_char = self._column_type in ['char', 'varchar']

        # make sense of the default
        if self._default and len(self._default) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip("'")
        elif self._default:
            if self._default.lower() == 'null':
                self._default = None
            elif self.is_char:
                self._parsing_warnings.append('Default value for column %s should be quoted' % self._name)
