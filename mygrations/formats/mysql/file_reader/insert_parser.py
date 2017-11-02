from mygrations.core.parse.parser import parser
from mygrations.formats.mysql.definitions.rows import rows

from .parsers.insert_values import insert_values

class insert_parser( parser, rows ):

    rules = [
        { 'type': 'literal', 'value': 'INSERT INTO' },
        { 'type': 'regexp', 'value': '[^\s\(]+', 'name': 'table' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'delimited', 'name': 'columns', 'separator': ',', 'quote': '`' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': 'VALUES' },
        { 'type': 'children', 'name': 'inserts', 'classes': [ insert_values ] },
        { 'type': 'literal', 'value': ';', 'optional': True, 'name': 'closing_semicolon' }
    ]

    def __init__( self, rules = [] ):

        super().__init__( rules )

        self._columns = []
        self._raw_rows = []

    def process( self ):

        self._table = self._values['table'].strip( '`' )
        self._columns = self._values['columns']
        self._raw_rows = []
        self._num_explicit_columns = len( self._columns ) if self._columns else 0
        self._errors = []
        self._warnings = []
        self.has_semicolon = True if 'closing_semicolon' in self._values else False

        had_comma = True
        for row in self._values['inserts']:

            if not had_comma:
                self._warnings.append( 'Missing comma between insert value groups' )

            if self._num_explicit_columns and len( row.values ) != self._num_explicit_columns:
                self._errors.append( 'Insert values has wrong number of values for %s' % ( row ) )
                continue

            self._raw_rows.append( row.values )
            had_comma = True if row.has_comma else False
