from mygrations.core.parse.parser import Parser
from mygrations.formats.mysql.definitions.index import Index
class IndexUnique(Parser, Index):

    _index_type = 'unique'
    has_comma = False

    # UNIQUE account_id (account_id)
    rules = [{
        'type': 'literal',
        'value': 'UNIQUE'
    }, {
        'type': 'regexp',
        'name': 'index_name',
        'value': '(KEY)|(INDEX)'
    }, {
        'type': 'regexp',
        'name': 'name',
        'value': '[^\(]+'
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
        'value': ',',
        'optional': True,
        'name': 'ending_comma'
    }]

    def process(self):

        self._name = self._values['name'].strip().strip('`')
        self._columns = self._values['columns']
        self.has_comma = True if 'ending_comma' in self._values else False
