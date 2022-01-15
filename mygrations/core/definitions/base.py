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
