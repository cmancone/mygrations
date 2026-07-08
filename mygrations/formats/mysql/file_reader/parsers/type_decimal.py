from mygrations.core.parse.parser import Parser
from .type import Type


class TypeDecimal(Parser, Type):
    allowed_types = {"real": True, "double": True, "float": True, "decimal": True, "numeric": True}

    decimals = ""

    # longitude float(20,4) unsigned default null
    rules = [
        {"type": "regexp", "value": "[^\(\s\)]+", "name": "name"},
        {"type": "regexp", "value": "\w+", "name": "type"},
        {"type": "literal", "value": "("},
        {"type": "regexp", "value": "\d+", "name": "length"},
        {"type": "literal", "value": ",", "name": "separating_comma"},
        {"type": "regexp", "value": "\d+", "name": "decimals"},
        {"type": "literal", "value": ")"},
        {"type": "literal", "value": "UNSIGNED", "optional": True},
        {"type": "literal", "value": "NULL", "optional": True, "name": "bare_null"},
        {"type": "literal", "value": "NOT NULL", "optional": True},
        {"type": "regexp", "value": "DEFAULT ([^\(\s\),]+)", "optional": True, "name": "default"},
        {"type": "literal", "value": ",", "optional": True, "name": "ending_comma"},
    ]

    def process(self):

        self._init_errors()
        self._name = self._extract_name()
        self._column_type = self._values["type"]
        self.decimals = self._values["decimals"]
        self._length = "%s,%s" % (self._values["length"], self._values["decimals"])
        self._unsigned = "UNSIGNED" in self._values
        self._has_default = "default" in self._values
        self._null = self._extract_null()
        self._default = self._values.get("default")

        # make sense of the default
        if self._default and len(self._default) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip("'")
            self._parsing_warnings.append(
                "Column '%s' has a numeric type but its default value is a string" % self._name
            )
        elif self._default and self._default.lower() == "null":
            self._default = None
