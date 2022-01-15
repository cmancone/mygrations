from mygrations.core.parse.parser import Parser
from mygrations.formats.mysql.definitions.index import Index
class IndexPrimary(Parser, Index):

    _index_type = 'primary'
    has_comma = False

    # PRIMARY KEY (`id`),
    rules = [{
        'type': 'literal',
        'value': 'PRIMARY KEY'
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

        self._name = ''
        self._columns = self._values['columns']
        self.has_comma = True if 'ending_comma' in self._values else False
