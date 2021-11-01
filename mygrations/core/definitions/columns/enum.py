from .string import String
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
        default: Union[str, int] = None,
        unsigned: bool = None,
        character_set: str = None,
        collate: str = None,
        auto_increment: bool = False,
        values: List[str] = None,
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
            default=default,
            character_set=character_set,
            collate=collate,
            auto_increment=auto_increment,
            values=values,
            parsing_errors=parsing_errors,
            parsing_warnings=parsing_warnings,
        )

    def find_schema_errors(self):
        errors = super().find_schema_errors()

        # exception because this is a parsing mistake, not an end-user mistake
        if not self.values or type(self.values) != list:
            raise ValueError(f"column '{self.name}' of type '{self.column_type}' must have a list of values")

        if self.default is not None and self.default and self.default not in self.values:
            errors.append(
                f"Default value for '{self.column_type}' column '{self.name}' is not in the list of allowed values"
            )

        return errors
