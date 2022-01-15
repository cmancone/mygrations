from collections import OrderedDict

from mygrations.core.parse.parser import Parser
from mygrations.formats.mysql.definitions.constraint import Constraint
from mygrations.formats.mysql.definitions.index import Index
from mygrations.formats.mysql.definitions.table import Table

from .parsers import *
class CreateParser(Table, Parser):

    # this defines the rules for the parsing engine.  Yes, I decided to try to build
    # a parsing engine to parse the MySQL.  Seems like a reasonable choice at the
    # moment, but we'll see how it works out in the long run.  The setup you see here
    # is a compromise between the declarative programming principles I like and the
    # time it takes to actually build such a system, especially for a relatively
    # limited use-case.  In the long run if this works well it could probably
    # become its own multi-purpose tool.  These "rules" basically boil down to:
    #
    # CREATE TABLE table_name ( [definitions] ) [options];
    #
    # definitions and options have their own patterns of allowed values and rules,
    # which also have to be defined.  That is handled below for the sake of brevity
    rules = [{
        'type': 'literal',
        'value': 'CREATE TABLE'
    }, {
        'type': 'regexp',
        'value': '\S+',
        'name': 'name'
    }, {
        'type': 'literal',
        'value': '('
    }, {
        'type':
        'children',
        'name':
        'definitions',
        'classes': [
            IndexPrimary, IndexKey, IndexUnique, ConstraintForeign, TypeCharacter, TypeNumeric, TypeDecimal, TypeText,
            TypeEnum, TypePlain
        ]
    }, {
        'type': 'literal',
        'value': ')'
    }, {
        'type': 'children',
        'name': 'table_options',
        'classes': [TableOption],
        'optional': True
    }, {
        'type': 'literal',
        'value': ';',
        'optional': True,
        'name': 'closing_semicolon'
    }]

    def process(self):

        self.semicolon = True if 'closing_semicolon' in self._values else False
        self._name = self._values['name'].strip('`')
        self._definitions = self._values['definitions']
        self._options = self._values['table_options'] if 'table_options' in self._values else []
        self._columns = OrderedDict()
        self._indexes = OrderedDict()
        self._constraints = OrderedDict()
        self._primary = ''

        # ignore the AUTO_INCREMENT option: there is no reason for us to ever manage that
        self._options = [opt for opt in self._options if opt.name != 'AUTO_INCREMENT']

        for definition in self._definitions:
            if hasattr(definition, 'as_definition'):
                if definition._name in self._columns:
                    self._global_errors.append(f"Table '{self._name}' has two columns named '{definition._name}'")
                    continue

                self.add_column(definition.as_definition())    # see notes on definition.as_definition()
            elif isinstance(definition, Index):
                if definition._name in self._indexes:
                    self._global_errors.append(f"Table '{self._name}' has two indexes named '{definition._name}'")
                    continue

                self.add_index(definition)
            elif isinstance(definition, Constraint):
                if definition._name in self._constraints:
                    self._global_errors.append(f"Table '{self._name}' has two constraints named '{definition._name}'")
                    continue

                self.add_constraint(definition)

            else:
                raise ValueError("Found unknown definition of type ".definition.__class__)

        if not self.semicolon:
            self._global_errors.append("Missing ending semicolon for table %s" % self._name)
