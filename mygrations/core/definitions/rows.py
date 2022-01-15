from __future__ import annotations
from typing import Union, List
from .columns.column import Column
class Rows:
    _columns: List[Column] = None
    _schema_errors: List[str] = None
    _schema_warnings: List[str] = None
    _parsing_errors: List[str] = None
    _parsing_warnings: List[str] = None
    _num_explicit_columns: int = 0
    _raw_rows: List[List[str]] = ''
    _table: str = ''
    _warnings: List[str] = None

    def __init__(
        self, table: str = '', raw_rows: List[List[str]] = [], columns: List[Column] = None, num_explicit_columns=0
    ):
        self._columns = columns if columns is not None else []
        self._schema_errors = []
        self._schema_warnings = []
        self._parsing_errors = []
        self._parsing_warnings = []
        self._num_explicit_columns = num_explicit_columns
        self._raw_rows = raw_rows
        self._table = table
        self._warnings = []

    @property
    def table(self) -> str:
        """ Returns the name of the table that records are being inserted for

        :returns: The name of the table
        """
        return self._table

    @property
    def raw_rows(self) -> List[List[str]]:
        """ Returns a list of insert values from the VALUES part of the query

        :returns: A list of values for each row
        """
        return self._raw_rows

    @property
    def columns(self) -> List[Column]:
        """ Returns the list of columns for the rows

        :returns: A list of columns
        """
        return self._columns

    @property
    def num_explicit_columns(self) -> int:
        """ Returns the number of columns specified in the insert query

        Can be zero if none are specified, which happens for queries like:
        INSERT INTO table (val1, val2, val3...);

        :returns: The number of columns which have been explicitly defined
        """
        return self._num_explicit_columns

    @property
    def schema_errors(self) -> List[str]:
        """ Returns a list of schema errors """
        return [] if self._schema_errors is None else self._schema_errors

    @property
    def schema_warnings(self) -> List[str]:
        """ Returns a list of schema warnings """
        return [] if self._schema_warnings is None else self._schema_warnings

    @property
    def parsing_errors(self) -> List[str]:
        """ Returns a list of parsing errors """
        return [] if self._parsing_errors is None else self._parsing_errors

    @property
    def parsing_warnings(self) -> List[str]:
        """ Returns a list of parsing warnings """
        return [] if self._parsing_warnings is None else self._parsing_warnings
