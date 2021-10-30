from .string import String
class Enum(String):
    _allowed_column_types = [
        'ENUM',
        'SET',
    ]

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
