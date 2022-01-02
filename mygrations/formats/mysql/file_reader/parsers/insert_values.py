from mygrations.core.parse.parser import Parser
class InsertValues(Parser):

    has_comma = False
    values = []

    rules = [{
        'type': 'literal',
        'value': '('
    }, {
        'type': 'delimited',
        'name': 'values',
        'separator': ',',
        'quote': "'"
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

        self.values = [
            str(val).replace('\\\\', '\\').replace("\\'", "'") if val != 'NULL' else None
            for val in self._values['values']
        ]
        self.has_comma = True if 'ending_comma' in self._values else False
