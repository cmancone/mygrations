from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, List
from .columns.column import Column


class Index:
    _name: str = ''
    _index_type: str = ''
    _columns: List[Union[Column, str]] = None
    _errors: List[str] = None
    _warnings: List[str] = None

    def __init__(self, name: str, columns: List[Union[Column, str]], index_type: str='INDEX'):
        """ Index constructor

        :param name: The name of the index
        :param columns: The columns in the index
        :param index_type: The type of the index (INDEX, UNIQUE, or PRIMARY)
        """
        self._name = name
        self._index_type = index_type
        self._columns = columns
        self._check_for_errors_and_warnings()

    @property
    def name(self) -> str:
        """ Public getter.  Returns the name of the column.

        :returns: The index name
        """
        return self._name

    @property
    def index_type(self) -> str:
        """ Public getter.  Returns a string denoting the type of the index.  Always returns in uppercase

        Index type can be 'INDEX', 'UNIQUE', or 'PRIMARY'

        :returns: The index type
        """
        return self._index_type.upper()

    def is_primary(self) -> bool:
        """ Returns True/False to denote if the index is a primary index """
        return self.index_type == 'PRIMARY'

    @property
    def columns(self) -> List[Union[Column, str]]:
        """ Public getter.  Returns a list of the columns and/or names on the index.

        :returns: The column length
        """
        return self._columns

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
        self._errors = []
        self._warnings = []
        for required in ['name', 'index_type', 'columns']:
            if not getattr(self, required):
                self._errors.append(f"Missing {required} for index {self.name}")
        if len(self.name) > 64:
            self._errors.append('Key name %s must be <=64 characters long' % (self._name))


    def __str__(self):
        """ Returns the MySQL command that would create the index

        i.e. PRIMARY KEY `id` (`id`)'

        :returns: A partial MySQL command that could be used to generate the column
        :rtype: string
        """
        parts = []
        if self.index_type == 'PRIMARY':
            parts.append('PRIMARY')
        elif self.index_type == 'UNIQUE':
            parts.append('UNIQUE')
        parts.append('KEY')

        if self.name:
            parts.append('`%s`' % self.name)
        parts.append('(`%s`)' % ("`,`".join(col if type(col) == str else col.name for col in self.columns)))

        return ' '.join(parts)
