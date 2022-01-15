from mygrations.core.parse.parser import Parser
from mygrations.formats.mysql.definitions.rows import Rows
from .parsers.insert_values import InsertValues
class InsertParser(Parser, Rows):

    rules = [{
        'type': 'literal',
        'value': 'INSERT INTO'
    }, {
        'type': 'regexp',
        'value': '[^\s\(]+',
        'name': 'table'
    }, {
        'type': 'literal',
        'value': '('
    }, {
        'type': 'delimited',
        'name': 'columns',
        'separator': ',',
        'quote': '`'
    }, {
        'type': 'literal',
        'value': ')'
    }, {
        'type': 'literal',
        'value': 'VALUES'
    }, {
        'type': 'children',
        'name': 'inserts',
        'classes': [InsertValues]
    }, {
        'type': 'literal',
        'value': ';',
        'optional': True,
        'name': 'closing_semicolon'
    }]

    def process(self):

        self._table = self._values['table'].strip('`')
        self._columns = self._values['columns']
        self._raw_rows = []
        self._num_explicit_columns = len(self._columns) if self._columns else 0
        self._schema_errors = []
        self._schema_warnings = []
        self._parsing_errors = []
        self._parsing_warnings = []
        self.has_semicolon = True if 'closing_semicolon' in self._values else False

        had_comma = True
        for row in self._values['inserts']:

            if not had_comma:
                self._parsing_warnings.append('Missing comma between insert value groups')

            if self._num_explicit_columns and len(row.values) != self._num_explicit_columns:
                self._parsing_errors.append('Insert values has different number of columns and values for %s' % (row))
                continue

            self._raw_rows.append(row.values)
            had_comma = True if row.has_comma else False
