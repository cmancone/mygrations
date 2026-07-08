from mygrations.formats.mysql.definitions import columns
from mygrations.core.definitions.columns.column import Column


class Type:
    @staticmethod
    def _unquote(value):
        """Strip surrounding single quotes from *value* if present.

        Returns the stripped string, or the original value unchanged if
        it is not quoted.
        """
        if value and len(value) >= 2 and value[0] == "'" and value[-1] == "'":
            return value.strip("'")
        return value

    def _init_errors(self):
        """Initialise the parsing/schema error and warning lists."""
        self._parsing_errors = []
        self._parsing_warnings = []
        self._schema_errors = []
        self._schema_warnings = []

    def _extract_name(self):
        """Return the column name with surrounding backticks removed."""
        return self._values["name"].strip("`")

    def _extract_null(self):
        """Return False when NOT NULL is present, True otherwise."""
        return False if "NOT NULL" in self._values else True

    column_type_map = {
        "INTEGER": columns.Numeric,
        "INT": columns.Numeric,
        "SMALLINT": columns.Numeric,
        "TINYINT": columns.Numeric,
        "MEDIUMINT": columns.Numeric,
        "BIGINT": columns.Numeric,
        "DECIMAL": columns.Numeric,
        "NUMERIC": columns.Numeric,
        "FLOAT": columns.Numeric,
        "DOUBLE": columns.Numeric,
        "BIT": columns.Numeric,
        "BOOLEAN": columns.Numeric,
        "BOOL": columns.Numeric,
        "DATE": columns.Date,
        "DATETIME": columns.Date,
        "TIMESTAMP": columns.Date,
        "TIME": columns.Date,
        "YEAR": columns.Date,
        "CHAR": columns.String,
        "VARCHAR": columns.String,
        "BINARY": columns.String,
        "VARBINARY": columns.String,
        "TINYBLOB": columns.String,
        "BLOB": columns.String,
        "MEDIUMBLOB": columns.String,
        "LONGBLOB": columns.String,
        "TINYTEXT": columns.String,
        "TEXT": columns.String,
        "MEDIUMTEXT": columns.String,
        "LONGTEXT": columns.String,
        "JSON": columns.String,
        "ENUM": columns.Enum,
        "SET": columns.Enum,
    }

    # MySQL type synonyms: map the synonym to the canonical name that
    # SHOW CREATE TABLE produces.  This prevents false-positive CHANGE
    # operations when the SQL file uses the synonym form.
    #
    # BOOLEAN/BOOL are intentionally absent — TypePlain.process() handles
    # them separately because they also require length normalisation (→ TINYINT(1))
    # and default value mapping (TRUE→1, FALSE→0).
    _type_synonyms = {
        "integer": "int",
    }

    @classmethod
    def _normalize_type(cls, raw_type: str) -> str:
        """Return the canonical MySQL type name for *raw_type*.

        For example ``INTEGER`` is normalised to ``int`` because MySQL's
        ``SHOW CREATE TABLE`` always emits ``int``.
        """
        return cls._type_synonyms.get(raw_type.lower(), raw_type)

    def as_definition(self) -> Column:
        """
        Returns the parsed column as a MySQL Column Definition

        This is here because a single parser class can end up working for columns of completely different
        types.  Therefore, we can't put the column definition directly in our inheritence tree and have
        to build and return a new one based on the type we have.
        """
        column_type = self._column_type.upper()
        if column_type not in self.column_type_map:
            raise ValueError(
                f"Found an unknown column type, '{column_type}' that does not have a corresponding column class"
            )
        column_class = self.column_type_map[column_type]
        return column_class(
            name=self._name,
            column_type=column_type,
            length=getattr(self, "_length", None),
            null=getattr(self, "_null", None),
            has_default=getattr(self, "_has_default", False),
            default=getattr(self, "_default", None),
            unsigned=getattr(self, "_unsigned", None),
            character_set=getattr(self, "_character_set", None),
            collate=getattr(self, "_collate", None),
            auto_increment=getattr(self, "_auto_increment", None),
            enum_values=getattr(self, "enum_values", None),
            parsing_errors=getattr(self, "_parsing_errors", None),
            parsing_warnings=getattr(self, "_parsing_warnings", None),
        )
