from .column import Column
from typing import List, Union

class Numeric(Column):
    _allowed_column_types = [
        'INTEGER',
        'INT',
        'SMALLINT',
        'TINYINT',
        'MEDIUMINT',
        'BIGINT',
        'DECIMAL',
        'NUMERIC',
        'FLOAT',
        'DOUBLE',
        'BIT',
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

        allow_float = ['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE']
        no_length = ['FLOAT', 'DOUBLE', 'BIT']
        no_auto_increment = ['FLOAT', 'DOUBLE', 'BIT']

        if self.default is not None and type(self.default) == str:
            self._schema_errors.append(
                f"Column '{self.name}' of type '{self.column_type}' cannot have a string value as a default"
            )
        else:
            if type(self.default) == float and self.column_type not in allow_float:
                self._schema_errors.append(
                    f"Column '{self.name}' of type '{self.column_type}' must have an integer value as a default"
                )
            if self.column_type == 'BIT' and self.default != 0 and self.default != 1:
                self._schema_errors.append(f"Column '{self.name}' of type 'BIT' must have a default of 1 or 0")

        if self.length:
            if self.column_type in no_length:
                self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a length")
            elif type(self.length) == str and ',' in self.length and self.column_type not in allow_float:
                self._schema_errors.append(
                    f"Column '{self.name}' of type '{self.column_type}' must have an integer value as its length"
                )

        if self.character_set is not None:
            self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a character set")
        if self.collate is not None:
            self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a collate")

        if self.auto_increment and self.column_type in no_auto_increment:
            self._schema_errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot be an AUTO_INCREMENT")

        if self.enum_values:
            self._schema_errors.append(
                "Column '%s' of type %s is not allowed to have a list of values for its length" %
                (self.name, self.column_type)
            )

    def _is_really_the_same_default(self, column: Column) -> bool:
        if self.column_type != 'DECIMAL':
            return super(Numeric, self)._is_really_the_same_default(column)

        # Default equality is mildly tricky for decimals because 0 and 0.000 are the same,
        # and if there are 4 digits after the decimal than 0.0000 and 0.00001 are the same too
        # This will come up if someone sets a default in an SQL file with too many (or too few) decimals,
        # while MySQL will report it properly rounded to the exact number of decimal places
        split = self.length.split(',')
        if len(split) == 2:
            ndecimals = int(split[1])
            if round(float(self.default), ndecimals) != round(float(column.default), ndecimals):
                return False
            return True

        return self.default == column.default
