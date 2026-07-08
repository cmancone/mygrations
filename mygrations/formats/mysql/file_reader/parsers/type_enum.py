from mygrations.core.parse.parser import Parser
from .type import Type


class TypeEnum(Parser, Type):
    allowed_types = {"set": True, "enum": True}

    values = []

    # types enum( `young`,`middle`,`old` )
    rules = [
        {"type": "regexp", "value": "[^\(\s\)]+", "name": "name"},
        {"type": "regexp", "value": "\w+", "name": "type"},
        {"type": "literal", "value": "("},
        {"type": "delimited", "name": "enum_values", "quote": "'", "separator": ","},
        {"type": "literal", "value": ")"},
        {"type": "literal", "value": "NULL", "optional": True, "name": "bare_null"},
        {"type": "literal", "value": "NOT NULL", "optional": True},
        {"type": "regexp", "value": "DEFAULT ([^\(\s\),]+)", "optional": True, "name": "default"},
        {"type": "regexp", "value": "CHARACTER SET ([^\(\s\),]+)", "name": "character_set", "optional": True},
        {"type": "regexp", "value": "COLLATE ([^\(\s\),]+)", "name": "collate", "optional": True},
        {"type": "literal", "value": ",", "optional": True, "name": "ending_comma"},
    ]

    def process(self):

        self._init_errors()
        self._name = self._extract_name()
        self._column_type = self._values["type"]
        self._enum_values = self._values["enum_values"]
        self._length = self._enum_values
        self._null = self._extract_null()
        self._has_default = "default" in self._values
        self._default = self._values.get("default")
        self._character_set = self._unquote(self._values.get("character_set"))
        self._collate = self._unquote(self._values.get("collate"))

        # make sense of the default
        if self._default and len(self._default) >= 2 and self._default[0] == "'" and self._default[-1] == "'":
            self._default = self._default.strip("'")
        elif self._default:
            if self._default.lower() == "null":
                self._default = None
            else:
                self._parsing_warnings.append(
                    'Default value of "%s" should have quotes for field %s' % (self._default, self._name)
                )
