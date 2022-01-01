from mygrations.core.parse.parser import Parser
from mygrations.core.definitions.option import Option

class TableOption(Option, Parser):

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

    def __init__(self):
        super().__init__('', '')

    def process(self):
        self._name = self._values['name'].strip()
        self._value = self._values['value'].strip()
