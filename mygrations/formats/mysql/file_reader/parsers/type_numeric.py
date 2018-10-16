from mygrations.core.parse.parser import parser
from mygrations.formats.mysql.definitions.column import column
class type_numeric(parser, column):

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

        self._errors = []
        self._warnings = []
        self.has_comma = True if 'ending_comma' in self._values else False

        self._name = self._values['name'].strip('`')
        self._column_type = self._values['type']
        self._length = self._values['length']
        self._unsigned = True if 'UNSIGNED' in self._values else False
        self._null = False if 'NOT NULL' in self._values else True
        self._default = self._values['default'] if 'default' in self._values else None
        self._auto_increment = True if 'AUTO_INCREMENT' in self._values else False
        self.is_char = self._column_type in ['char', 'varchar']

        # double check unsigned
        if self._unsigned and self.is_char:
            self._errors.append("Column %s is a character type and cannot be unsigned" % self._name)

        # make sense of the default
        if self._default and len(self._default) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip("'")
            if not self.is_char:
                self._warnings.append('Default value for numeric column %s does not need to be quoted' % self._name)
        elif self._default:
            if self._default.lower() == 'null':
                self._default = None
            elif self.is_char:
                self._warnings.append('Default value for column %s should be quoted' % self._name)

        if self._default is None and not self._null and not self._auto_increment:
            self._warnings.append(
                'Column %s is not null and has no default: you should set a default to avoid MySQL warnings' %
                (self._name)
            )

        if self._auto_increment and self.is_char:
            self._errors.append(
                'Column %s is an auto increment character field: only numeric fields can auto increment' % (self._name)
            )

        # only a few types of field are allowed to have decimals
        if not self._column_type.lower() in self.allowed_types:
            self._errors.append(
                'Column of type %s is not allowed to have a length for column %s' % (self._column_type, self._name)
            )
