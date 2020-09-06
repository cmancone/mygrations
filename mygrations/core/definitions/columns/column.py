from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, List


class Column(ABC):
    _auto_increment: bool = None
    _character_set: str = None
    _collate: str = None
    _column_type: str = None
    _default: Union[str, int] = None
    _length: Union[str, int] = None
    _name: str = ''
    _null: bool = None
    _unsigned: bool = None
    _errors: List[str] = None
    _warnings: List[str] = None
    _allowed_column_types = []
    _values: List[str] = None # enum/set only

    def __init__(
        self,
        name: str,
        column_type: str,
        length: Union[str, int] = None,
        null: bool = True,
        default: Union[str, int] = None,
        unsigned: bool = None,
        character_set: str = None,
        collate: str = None,
        auto_increment: bool = False,
        values: List[str] = None,
    ):
        self._auto_increment = auto_increment
        self._character_set = character_set
        self._collate = collate
        self._column_type = column_type
        self._default = default
        self._length = length
        self._name = name
        self._null = null
        self._unsigned = unsigned
        self._values = values
        self._check_for_errors_and_warnings()

    @property
    def name(self) -> str:
        """ Public getter.  Returns the name of the column.

        :returns: The column name
        """

        return self._name

    @property
    def length(self) -> Union[str, int]:
        """ Public getter.  Returns the length of the column as a string.

        Some examples of the length for various column definitions:

        ==================  ====================
        Type                Length
        ==================  ====================
        INT(10) UNSIGNED    10
        VARCHAR(255)        255
        decimal(20,5)       20,5
        date
        ==================  ====================

        :returns: The column length
        """

        return self._length

    @property
    def null(self) -> bool:
        """ Public getter.  Returns True/False to denote if the column is allowed to be null

        :returns: Whether or not null is an allowed value for the column
        """
        return self._null

    @property
    def column_type(self) -> str:
        """ Public getter.  Returns a string denoting the type of the column.  Always returns in uppercase

        Some examples of the length for various column definitions:

        ==================  ====================
        Definition          Type
        ==================  ====================
        INT(10) UNSIGNED    INT
        VARCHAR(255)        VARCHAR
        decimal(20,5)       DECIMAL
        date                DATE
        ==================  ====================

        :returns: The column type
        """
        return self._column_type.upper()

    @property
    def default(self) -> Union[str, int]:
        """ Public getter.  Returns the default value for the column as a string, or None for a default value of null

        Returns None to represent a default value of null.

        :returns: The default value
        """
        return self._default

    @property
    def unsigned(self) -> bool:
        """ Public getter.  Returns True, False, or None to denote the status of the UNSIGNED property

        ==================  ====================
        Return Value        Meaning
        ==================  ====================
        True                The column is unsigned
        False               The column is signed
        None                UNSIGNED is not an applicable property for this column type
        ==================  ====================

        :returns: True, False, or None
        """
        return self._unsigned

    @property
    def character_set(self) -> str:
        """ Public getter.  Returns None or a value to denote the CHARACTER_SET property

        :returns: string, or None
        """
        return None if self._character_set is None else self._character_set.upper()

    @property
    def collate(self) -> str:
        """ Public getter.  Returns None or a value to denote the COLLATE property

        :returns: string, or None
        """
        return None if self._collate is None else self._collate.upper()

    @property
    def auto_increment(self) -> bool:
        """ Public getter.  Returns True, False, or None to denote the status of the AUTO_INCREMENT property

        ==================  ====================
        Return Value        Meaning
        ==================  ====================
        True                The column is an AUTO_INCREMENT column
        False               The column is not an AUTO_INCREMENT column
        None                AUTO_INCREMENT is not an applicable property for this column type
        ==================  ====================

        :returns: True, False, or None
        """
        return self._auto_increment

    @property
    def values(self) -> List[str]:
        """ Public getter.  Returns the allowed values for the column (enum/set only)"""
        return self._values

    @property
    def errors(self) -> List[str]:
        """ Public getter.  Returns a list of parsing errors

        :returns: A list of parsing errors
        """
        return [] if self._errors is None else self._errors

    @property
    def warnings(self) -> List[str]:
        """ Public getter.  Returns a list of parsing/table warnings

        :returns: A list of parsing/table warnings
        """
        return [] if self._warnings is None else self._warnings

    def _check_for_errors_and_warnings(self):
        """ Runs through the properties of the column and populates self._errors and self._warnings approppriately """

        # we raise an exception (instead of recording an error) if the column type is invalid for the current
        # class because this represents a bug in mygrations.  I.e. if an INT column_type ends up in the
        # String() column, then something went wrong with mygrations, not with the SQL the user wrote.
        if self.column_type not in self._allowed_column_types:
            raise ValueError(f'Error in column {self.name}: column type {self.column_type} not allowed for class {self.__class__.__name__}')

        self._errors = []
        self._warnings = []
        if self.default is None and not self.null:
            self._warnings.append(f'Column {self.name} is not null and has no default')

        for required in ['name', 'column_type']:
            if not getattr(self, required):
                self._errors.append(f"Missing {required} for column {self.name}")


    def __str__(self) -> str:
        """ Returns the MySQL command that would create the column

        i.e. column_name type(len) default ''

        :returns: A partial MySQL command that could be used to generate the column
        """
        parts = []
        parts.append('`%s`' % self.name)

        type_string = self.column_type
        if self.values:
            type_string += "('%s')" % ("', '".join(self.values))
        elif self.length is not None:
            type_string += '(%s)' % self.length
        parts.append(type_string)

        if self.unsigned:
            parts.append('UNSIGNED')

        if not self.null:
            parts.append('NOT NULL')

        if self.default is not None:
            if self.default == '':
                parts.append("DEFAULT ''")
            elif type(self.default) != str or self.default.isnumeric():
                parts.append("DEFAULT %s" % self.default)
            else:
                parts.append("DEFAULT '%s'" % self.default)

        if self.auto_increment:
            parts.append('AUTO_INCREMENT')

        return ' '.join(parts)

    def is_really_the_same_as(self, column: Column) -> bool:
        """ Takes care of a pesky false-positive when checking columns

        :param column: The column to comprehensively check for a difference with
        :returns: True if the column really is the same, even for apparent differences
        """
        # if any of these attributes change then it really isn't the same
        for attr in ['name', 'length', 'null', 'column_type', 'unsigned']:
            if getattr(self, attr) != getattr(column, attr):
                return False

        if self._default_none_mismatch(column):
            return False
        if not self._is_really_the_same_default(column):
            return False

        # if we got here then these columns are the same. Either all attributes have the same
        # values, or collate and/or character_set differ, but they differ by one not having
        # a value.  This is the false-positive we are trying to check for
        # (see tests.formats.mysql.definitions.test_table_text_false_positives)
        return True

    def _default_none_mismatch(self, column: Column) -> bool:
        if self.default is not None and column.default is None:
            return True
        if column.default is not None and self.default is None:
            return True
        return False

    def _is_really_the_same_default(self, column: Column) -> bool:
        return self.default == column.default
