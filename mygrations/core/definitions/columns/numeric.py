from .column import Column
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

    def find_schema_errors(self):
        errors = super().find_schema_errors()

        allow_float = ['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE']
        no_length = ['FLOAT', 'DOUBLE', 'BIT']
        no_auto_increment = ['FLOAT', 'DOUBLE', 'BIT']

        if self.default is not None and type(self.default) == str:
            errors.append(
                f"Column '{self.name}' of type '{self.column_type}' cannot have a string value as a default"
            )
        else:
            if type(self.default) == float and self.column_type not in allow_float:
                errors.append(
                    f"Column '{self.name}' of type '{self.column_type}' must have an integer value as a default"
                )
            if self.column_type == 'BIT' and self.default != 0 and self.default != 1:
                errors.append(f"Column '{self.name}' of type 'BIT' must have a default of 1 or 0")

        if self.length:
            if self.column_type in no_length:
                errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a length")
            elif type(self.length) == str and ',' in self.length and self.column_type not in allow_float:
                errors.append(
                    f"Column '{self.name}' of type '{self.column_type}' must have an integer value as its length"
                )

        if self.character_set is not None:
            errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a character set")
        if self.collate is not None:
            errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot have a collate")

        if self.auto_increment and self.column_type in no_auto_increment:
            errors.append(f"Column '{self.name}' of type '{self.column_type}' cannot be an AUTO_INCREMENT")

        return errors

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
