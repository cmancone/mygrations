from mygrations.core.parse.parser import Parser
class TableOption(Parser):

    name = ''
    value = ''

    # UNIQUE account_id (account_id)
    rules = [{
        'type': 'regexp',
        'value': '[^=]{1,30}',
        'name': 'name'
    }, {
        'type': 'literal',
        'value': '='
    }, {
        'type': 'regexp',
        'value': '[^\s;]+',
        'name': 'value'
    }]

    def process(self):
        self._name = self._values['name'].strip()
        self._value = self._values['value'].strip()

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value
