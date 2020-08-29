from .column import Column


class String(Column):
    _allowed_column_types = [
        'CHAR',
        'VARCHAR',
        'BINARY',
        'VARBINARY',
        'TINYBLOB',
        'BLOB',
        'MEDIUMBLOB',
        'LONGBLOB',
        'TINYTEXT',
        'TEXT',
        'MEDIUMTEXT',
        'LONGTEXT',
        'JSON',
    ]

    _allowed_default = [
        'CHAR',
        'VARCHAR',
        'BINARY',
        'VARBINARY',
    ]

    _allowed_collation = [
        'CHAR',
        'VARCHAR',
        'BINARY',
        'VARBINARY',
    ]

    _allowed_length = [
        'CHAR',
        'VARCHAR',
        'BINARY',
        'VARBINARY',
    ]

    def __str__(self) -> str:
        as_string = super(String, self).__str__()
        if self.character_set:
            as_string += f" CHARACTER SET '{self.character_set}'"

        if self.collate:
            as_string += f" COLLATE '{self.collate}'"

        return as_string

    def _check_for_errors_and_warnings(self):
        super(String, self)._check_for_errors_and_warnings()
        if self.default is not None and self.column_type not in self._allowed_default:
            self._errors.append(f'Column {self.name} of type {self.column_type} cannot have a default')

        if (self.character_set or self.collate):
            if self.column_type not in self._allowed_collation
                self._errors.append(
                    f'Column {self.name} of type {self.column_type} cannot have a collation/character set'
                )
            is_binary = self.column_type == 'BINARY' or self.column_type == 'VARBINARY'
            binary_collation = 'BINARY' if self.collate is None else self.collate
            binary_character_set = 'BINARY' if self.character_set is None else self.character_set
            if is_binary and (binary_collation != 'BINARY' or binary_character_set != 'BINARY'):
                self._errors.append(
                    f'Column {self.name} of type {self.column_type} can only have a collate/character set of BINARY'
                )

        if self.length and self.column_type not in self._allowed_length:
            self._errors.append(f'Column {self.name} of type {self.column_type} cannot have a length')

    def is_really_the_same_as(self, column: Column) -> bool:
        if not super(String, self).is_really_the_same_as(column):
            return False

        # if collate or character_set are different and *both* have a value,
        # then these aren't really the same
        for attr in ['collate', 'character_set']:
            my_val = getattr(self, attr)
            that_val = getattr(column, attr)
            if my_val and that_val and my_val != that_val:
                return False

        return True
