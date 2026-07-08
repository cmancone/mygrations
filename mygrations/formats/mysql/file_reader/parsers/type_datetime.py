from mygrations.core.parse.parser import Parser
from .type import Type


class TypeDateTime(Parser, Type):
    allowed_collation_types = {"char": True, "varchar": True}

    # in this case we have much less disallowed than allowed
    disallowed_types = {
        "date": True,
        "year": True,
        "tinyblob": True,
        "blob": True,
        "mediumblob": True,
        "longblob": True,
        "tinytext": True,
        "text": True,
        "mediumtext": True,
        "longtext": True,
        "json": True,
    }

    # name varchar(255) NOT NULL DEFAULT '' CHARACTER SET uf8 COLLATE utf8
    # hackish? maybe (i.e. yes) the repeated COLLATE and CHARACTER SETS take care of uncertain
    # ordering.  I could also use `children` which is order-agnostic, but I'm being lazy
    rules = [
        {"type": "regexp", "value": "[^\(\s\)]+", "name": "name"},
        {"type": "regexp", "value": "\w+", "name": "type"},
        {"type": "regexp", "value": "COLLATE ([^\(\s\),]+)", "name": "collate", "optional": True},
        {"type": "regexp", "value": "CHARACTER SET ([^\(\s\),]+)", "name": "character_set", "optional": True},
        {"type": "regexp", "value": "COLLATE ([^\(\s\),]+)", "name": "collate", "optional": True},
        {"type": "literal", "value": "NULL", "optional": True, "name": "bare_null"},
        {"type": "literal", "value": "NOT NULL", "optional": True},
        {"type": "regexp", "value": "COLLATE ([^\(\s\),]+)", "name": "collate", "optional": True},
        {"type": "regexp", "value": "CHARACTER SET ([^\(\s\),]+)", "name": "character_set", "optional": True},
        {"type": "regexp", "value": "COLLATE ([^\(\s\),]+)", "name": "collate", "optional": True},
        {"type": "regexp", "value": "DEFAULT '([^']+)'", "optional": True, "name": "default"},
        {"type": "regexp", "value": 'DEFAULT "([^"]+)"', "optional": True, "name": "default"},
        {"type": "regexp", "value": "COLLATE ([^\(\s\),]+)", "name": "collate", "optional": True},
        {"type": "regexp", "value": "CHARACTER SET ([^\(\s\),]+)", "name": "character_set", "optional": True},
        {"type": "regexp", "value": "COLLATE ([^\(\s\),]+)", "name": "collate", "optional": True},
        {"type": "literal", "value": ",", "optional": True, "name": "ending_comma"},
    ]

    def process(self):

        self._init_errors()
        self._name = self._extract_name()
        self._column_type = self._values["type"]
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
            elif not self._default.isdigit():
                self._parsing_warnings.append(
                    'Default value of "%s" should have quotes for field %s' % (self._default, self._name)
                )

        self._attributes = {}
        if self._character_set:
            self._attributes["CHARACTER SET"] = self._character_set
        if self._collate:
            self._attributes["COLLATE"] = self._collate
