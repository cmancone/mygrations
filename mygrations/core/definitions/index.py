from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, List
from .columns.column import Column
class Index:
    _name: str = ''
    _index_type: str = ''
    _columns: List[str] = None
    _schema_errors: List[str] = None
    _schema_warnings: List[str] = None
    _parsing_errors: List[str] = None
    _parsing_warnings: List[str] = None

    def __init__(self, name: str = '', columns: List[str] = None, index_type: str = None):
        """ Index constructor

        :param name: The name of the index
        :param columns: The name of the columns in the index
        :param index_type: The type of the index (INDEX, UNIQUE, or PRIMARY)
        """
        self._name = name
        self._columns = [*columns] if columns else []
        self._schema_errors = None
        self._schema_warnings = None
        self._parsing_errors = None
        self._parsing_warnings = None
        # this is often set at the class level by a parser, so we only want to set it if provided
        if index_type is not None:
            self._index_type = index_type

    @property
    def name(self) -> str:
        """ Public getter.  Returns the name of the column.

        :returns: The index name
        """
        # if we don't have a name then assume it's name matches the name of our first column
        if self._name:
            return self._name
        if len(self._columns) > 0:
            return self._columns[0] if type(self._columns[0]) == str else self._columns[0].name
        return ''

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
    def columns(self) -> List[Column]:
        """ Returns a list of the columns on the index. """
        return self._columns

    @property
    def schema_errors(self) -> List[str]:
        """ Returns a list of schema errors """
        if self._schema_errors is None:
            self._check_for_schema_errors_and_warnings()
        return self._schema_errors

    @property
    def schema_warnings(self) -> List[str]:
        """ Returns a list of schema warnings """
        if self._schema_errors is None:
            self._check_for_schema_errors_and_warnings()
        return self._schema_warnings

    @property
    def parsing_errors(self) -> List[str]:
        """ Returns a list of parsing errors """
        return self._parsing_errors if self._parsing_errors is not None else []

    @property
    def parsing_warnings(self) -> List[str]:
        """ Returns a list of parsing/table warnings """
        return self._parsing_warnings if self._parsing_warnings is not None else []

    def _check_for_schema_errors_and_warnings(self):
        self._schema_errors = []
        self._schema_warnings = []
        for required in ['name', 'index_type', 'columns']:
            if not getattr(self, required):
                self._schema_errors.append(f"Missing {required} for index {self.name}")
        if len(self.name) > 64:
            self._schema_errors.append('Key name %s must be <=64 characters long' % (self._name))

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

        if self._name:
            parts.append('`%s`' % self.name)
        parts.append('(`%s`)' % ("`,`".join(self.columns)))

        return ' '.join(parts)
