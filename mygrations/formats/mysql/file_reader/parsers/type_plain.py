from mygrations.core.parse.parser import Parser
from .type import Type


class TypePlain(Parser, Type):
    _is_primary_key = False

    # created date
    # The NULL / NOT NULL rules are repeated before and after DEFAULT to support
    # both orderings (`NOT NULL DEFAULT x` and `DEFAULT x NOT NULL`), following
    # the same pattern used by TypeCharacter and TypeText for repeated optional rules.
    # "bare_null" tokens are parsed only to consume the NULL keyword from the
    # remaining input — the actual nullability logic in process() uses "NOT NULL".
    rules = [
        {"type": "regexp", "value": "[^\(\s\)]+", "name": "name"},
        {"type": "regexp", "value": "\w+", "name": "type"},
        {"type": "literal", "value": "UNSIGNED", "optional": True},
        # Consume bare NULL before DEFAULT so it doesn't confuse subsequent rules.
        {"type": "literal", "value": "NULL", "optional": True, "name": "bare_null"},
        {"type": "literal", "value": "NOT NULL", "optional": True},
        {"type": "literal", "value": "PRIMARY KEY", "optional": True},
        {
            "type": "regexp",
            "value": "DEFAULT ([^\(\s\),]+)",
            "optional": True,
            "name": "default",
        },
        # Consume bare NULL after DEFAULT for `DEFAULT x NULL` ordering.
        {"type": "literal", "value": "NULL", "optional": True, "name": "bare_null"},
        {"type": "literal", "value": "NOT NULL", "optional": True},
        {"type": "literal", "value": "PRIMARY KEY", "optional": True},
        {"type": "literal", "value": "AUTO_INCREMENT", "optional": True},
        {"type": "literal", "value": ",", "optional": True, "name": "ending_comma"},
    ]

    def process(self):

        self._init_errors()
        self._name = self._extract_name()
        self._length = ""
        self._column_type = self._normalize_type(self._values["type"])
        self._unsigned = "UNSIGNED" in self._values
        self._has_default = "default" in self._values
        self._default = self._unquote(self._values.get("default"))
        self._auto_increment = "AUTO_INCREMENT" in self._values
        self._is_primary_key = "PRIMARY KEY" in self._values

        if "NOT NULL" in self._values:
            self._null = False
        elif self._is_primary_key:
            # MySQL treats PRIMARY KEY columns as implicitly NOT NULL, and
            # SHOW CREATE TABLE always outputs the explicit NOT NULL.  Match
            # that behaviour so comparisons don't produce false-positive
            # CHANGE operations.
            self._null = False
        else:
            self._null = True

        if self._column_type.upper() in ("BOOLEAN", "BOOL"):
            self._column_type = "TINYINT"
            self._length = "1"
            if self._default is not None and self._default.upper() == "FALSE":
                self._default = "0"
            elif self._default is not None and self._default.upper() == "TRUE":
                self._default = "1"

        # make sense of the default
        if self._default and self._default.lower() == "null":
            self._default = None
