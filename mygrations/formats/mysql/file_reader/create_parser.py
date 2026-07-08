import re
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
    rules = [
        {"type": "literal", "value": "CREATE TABLE"},
        {
            "type": "literal",
            "value": "IF NOT EXISTS",
            "optional": True,
            "name": "if_not_exists",
        },
        {"type": "regexp", "value": "\S+", "name": "name"},
        {"type": "literal", "value": "("},
        {
            "type": "children",
            "name": "definitions",
            "classes": [
                IndexPrimary,
                IndexKey,
                IndexUnique,
                ConstraintForeign,
                ConstraintForeignBare,
                TypeCharacter,
                TypeNumeric,
                TypeDecimal,
                TypeEnum,
                TypePlain,
                TypeText,
                TypeDateTime,
            ],
        },
        {"type": "literal", "value": ")"},
        {
            "type": "children",
            "name": "table_options",
            "classes": [TableOption],
            "optional": True,
        },
        {
            "type": "literal",
            "value": ";",
            "optional": True,
            "name": "closing_semicolon",
        },
    ]

    def parse(self, string=""):
        # Strip inline -- comments before the base parser collapses whitespace.
        # parser.py:68 does re.sub('\s+', ' ', string) which turns newlines into
        # spaces, so '-- comment\ncolumn' becomes '-- comment column' and the
        # comment eats the next line. Stripping here prevents that.
        string = re.sub(r"--[^\n]*", "", string)
        # Strip index prefix-lengths like full_path(255) → full_path.
        # The delimited parser splits column lists on ')' which conflicts with
        # the inner ')' of prefix-lengths. We match word(digits) preceded by
        # '(' or ',' (index column-list context) which avoids type lengths like
        # INT(11) or VARCHAR(255) that are preceded by the type keyword.
        string = re.sub(r"(\(|\,)(\s*`?\w+`?)\(\d+\)", r"\1\2", string)
        return super().parse(string)

    def process(self):

        self.semicolon = True if "closing_semicolon" in self._values else False
        self._name = self._values["name"].strip("`")
        self._definitions = self._values["definitions"]
        self._options = self._values["table_options"] if "table_options" in self._values else []
        self._columns = OrderedDict()
        self._indexes = OrderedDict()
        self._constraints = OrderedDict()
        self._primary = ""

        # ignore the AUTO_INCREMENT option: there is no reason for us to ever manage that
        self._options = [opt for opt in self._options if opt.name != "AUTO_INCREMENT"]

        for definition in self._definitions:
            if hasattr(definition, "as_definition"):
                if definition._name in self._columns:
                    self._global_errors.append(f"Table '{self._name}' has two columns named '{definition._name}'")
                    continue

                self.add_column(definition.as_definition())  # see notes on definition.as_definition()

                if getattr(definition, "_is_primary_key", False):
                    primary_index = Index(name="", columns=[definition._name], index_type="primary")
                    self.add_index(primary_index)

            elif isinstance(definition, Index):
                if definition._name in self._indexes:
                    self._global_errors.append(f"Table '{self._name}' has two indexes named '{definition._name}'")
                    continue

                self.add_index(definition)
            elif isinstance(definition, Constraint):
                if isinstance(definition, ConstraintForeignBare):
                    fk_name = "%s_%s_%s_fk" % (
                        self._name,
                        definition._column_name,
                        definition._foreign_table_name,
                    )
                    definition._name = fk_name[:64]
                if definition._name in self._constraints:
                    self._global_errors.append(f"Table '{self._name}' has two constraints named '{definition._name}'")
                    continue

                self.add_constraint(definition)

                if isinstance(definition, ConstraintForeignBare):
                    col = definition._column_name
                    has_index = col in self._indexes or any(col in idx._columns for idx in self._indexes.values())
                    has_future_index = any(isinstance(d, Index) and col in d._columns for d in self._definitions)
                    if not has_index and not has_future_index:
                        self.add_index(Index(name=col, columns=[col], index_type="index"))

            else:
                raise ValueError(f"Found unknown definition of type {definition.__class__}")

        if not self.semicolon:
            self._global_errors.append("Missing ending semicolon for table %s" % self._name)
