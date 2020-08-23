from .column import Column


class String(Column):
    def __str__(self) -> str:
        as_string = super(String, self).__str__()
        if self.character_set:
            as_string += f" CHARACTER SET '{self.character_set}'"

        if self.collate:
            as_string += f" COLLATE '{self.collate}'"

        return as_string

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
