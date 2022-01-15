from .column import Column
from typing import List, Union
class Date(Column):
    _allowed_column_types = [
        'DATE',
        'DATETIME',
        'TIMESTAMP',
    ]

    def __init__(
        self,
        name: str = '',
        column_type: str = '',
        length: Union[str, int] = None,
        null: bool = True,
        has_default: bool = False,
        default: Union[str, int] = None,
        unsigned: bool = None,
        character_set: str = None,
        collate: str = None,
        auto_increment: bool = False,
        enum_values: List[str] = None,
        parsing_errors: List[str] = None,
        parsing_warnings: List[str] = None,
    ):
        # it would be nice to just do `def __init__(**kwargs)` and then `super().__init__(**kwargs)`
        # but then we would lose our type hints.  :shrug:
        super().__init__(
            name=name,
            column_type=column_type,
            length=length,
            null=null,
            has_default=has_default,
            default=default,
            unsigned=unsigned,
            character_set=character_set,
            collate=collate,
            auto_increment=auto_increment,
            enum_values=enum_values,
            parsing_errors=parsing_errors,
            parsing_warnings=parsing_warnings,
        )

    def _check_for_schema_errors_and_warnings(self):
        super()._check_for_schema_errors_and_warnings()

        if self.length:
            self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a length")

        if self.character_set is not None:
            self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a character set")
        if self.collate is not None:
            self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a collate")

        if self.auto_increment and self.column_type in no_auto_increment:
            self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot be an AUTO_INCREMENT")

        if self.values:
            self._schema_errors.append(
                "Column '%s' of type %s is not allowed to have a list of values for its length" %
                (self.name, self.column_type)
            )

        if self.unsigned:
            self._schema_errors.append("Column %s cannot be unsigned" % self._name)
