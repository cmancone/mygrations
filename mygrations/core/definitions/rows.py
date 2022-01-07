from __future__ import annotations
from typing import Union, List
from .columns.column import Column
class Rows:
    _columns: List[Column] = None
    _errors: List[str] = None
    _num_explicit_columns: int = 0
    _raw_rows: List[List[str]] = ''
    _table: str = ''
    _warnings: List[str] = None

    def __init__(self, table: str = '', raw_rows: List[List[str]] = [], columns: List[Column] = None, num_explicit_columns=0):
        self._columns = columns if columns is not None else []
        self._errors = []
        self._num_explicit_columns = num_explicit_columns
        self._raw_rows = raw_rows
        self._table = table
        self._warnings = []

    @property
    def table(self) -> str:
        """ Public getter.  Returns the name of the table that records are being inserted for

        :returns: The name of the table
        """
        return self._table

    @property
    def raw_rows(self) -> List[List[str]]:
        """ Public getter.  Returns a list of insert values from the VALUES part of the query

        :returns: A list of values for each row
        """
        return self._raw_rows

    @property
    def columns(self) -> List[Column]:
        """ Public getter.  Returns the list of columns for the rows

        :returns: A list of columns
        """
        return self._columns

    @property
    def num_explicit_columns(self) -> int:
        """ Public getter.  Returns the number of columns specified in the insert query

        Can be zero if none are specified, which happens for queries like:
        INSERT INTO table (val1, val2, val3...);

        :returns: The number of columns which have been explicitly defined
        """
        return self._num_explicit_columns

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
        :rtype: list
        """
        return [] if self._warnings is None else self._warnings
