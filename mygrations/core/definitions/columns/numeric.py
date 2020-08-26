from .column import Column


class Numeric(Column):
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
