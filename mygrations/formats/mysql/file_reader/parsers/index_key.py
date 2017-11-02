from mygrations.core.parse.parser import parser
from mygrations.formats.mysql.definitions.index import index

class index_key( parser, index ):

    _index_type = 'index'
    has_comma = False

    # KEY account_id (account_id,name)
    rules = [
        { 'type': 'literal', 'value': 'KEY' },
        { 'type': 'regexp', 'name': 'name', 'value': '[^\(\s\)]+' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'delimited', 'name': 'columns', 'separator': ',', 'quote': '`' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]

    def __init__( self, rules = [] ):

        super().__init__( rules )

        self._errors = []
        self._warnings = []
        self._columns = []

    def process( self ):

        self._name = self._values['name'].strip().strip( '`' )
        self._columns = self._values['columns']
        self.has_comma = True if 'ending_comma' in self._values else False

        if len( self.name ) > 64:
            self._errors.append( 'Key name %s is too long' % ( self.name ) )
