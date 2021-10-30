from __future__ import annotations
from typing import List

class Base:
    _parsing_errors = None
    _parsing_warnings = None

    @property
    def parsing_errors(self) -> List[str]:
        """ Public getter.  Returns a list of parsing errors """
        return self._parsing_errors if self._parsing_errors is not None else []

    @property
    def parsing_warnings(self) -> List[str]:
        """ Public getter.  Returns a list of parsing errors """
        return self._parsing_warnings if self._parsing_warnings is not None else []

    @property
    def errors(self) -> List[str]:
        """ Public getter. Returns a list of errors """
        return [
            *self.parsing_errors,
            *self.find_schema_errors(),
        ]

    @property
    def warnings(self) -> List[str]:
        """ Public getter.  Returns a list of warnings """
        return [
            *self.parsing_warnings,
            *self.find_schema_warnings(),
        ]

    def find_schema_errors(self) -> List[str]:
        """ Returns a list of schema errors """
        raise NotImplementedError()

    def find_schema_warnings(self) -> List[str]:
        """ Returns a list of schema warnings """
        raise NotImplementedError()
