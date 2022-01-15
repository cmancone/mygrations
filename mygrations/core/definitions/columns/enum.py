from .string import String
from typing import List, Union
class Enum(String):
    _allowed_column_types = [
        'ENUM',
        'SET',
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

        if not self.enum_values or type(self.enum_values) != list:
            self._schema_errors.append(f"column '{self.name}' of type '{self.column_type}' must have a list of values")

        if self.default and self.default not in self.enum_values:
            self._schema_errors.append(
                f"Default value for '{self.column_type}' column '{self.name}' is not in the list of allowed values"
            )

        if self.auto_increment and self.column_type in no_auto_increment:
            self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot be an AUTO_INCREMENT")

        if self.unsigned:
            self._schema_errors.append("Column %s cannot be unsigned" % self._name)
