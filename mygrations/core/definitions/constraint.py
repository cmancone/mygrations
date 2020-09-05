from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, List, Tuple


class Constraint:
    _column_name: str = ''
    _errors: List[str] = None
    _foreign_table: str = ''
    _foreign_column_name: str = ''
    _name: str = ''
    _on_delete: str = ''
    _on_update: str = ''
    _warnings: List[str] = None

    def __init__(
        self,
        name: str,
        column_name: str,
        foreign_table: str,
        foreign_column_name: str,
        on_delete: str = '',
        on_update: str = ''
    ):
        self._column_name = column_name
        self._foreign_table = foreign_table
        self._foreign_column_name = foreign_column_name
        self._name = name
        self._on_delete = on_delete.upper()
        self._on_update = on_update.upper()
        if not self._on_delete:
            self._on_delete = 'RESTRICT'
        if not self._on_update:
            self._on_update = 'RESTRICT'

        self._check_for_errors_and_warnings()

    @property
    def name(self) -> str:
        """ Public getter.  Returns the name of the constraint. """
        return self._name

    @property
    def column_name(self) -> str:
        """ Public getter.  Returns the name of the column this constraint is on """
        return self._column_name

    @property
    def foreign_table(self) -> str:
        """ Public getter.  Returns the name of the table this constraint is to """
        return self._foreign_table

    @property
    def foreign_column_name(self) -> str:
        """ Public getter.  Returns the name of the column in the foreign table this constraint is to """
        return self._foreign_column_name

    @property
    def on_delete(self) -> str:
        """ Public getter.  Returns the ON DELETE action for this constraint """
        return self._on_delete

    @property
    def on_update(self) -> str:
        """ Public getter.  Returns the ON UPDATE action for this constraint """
        return self._on_update

    @property
    def errors(self) -> List[str]:
        """ Public getter.  Returns a list of parsing errors """
        return [] if self._errors is None else self._errors

    @property
    def warnings(self) -> List[str]:
        """ Public getter.  Returns a list of parsing/table warnings """
        return [] if self._warnings is None else self._warnings

    def _check_for_errors_and_warnings(self):
        allowed_actions = ['CASCADE', 'NO ACTION', 'RESTRICT', 'SET DEFAULT', 'SET NULL']
        self._errors = []
        self._warnings = []
        if self.on_delete not in allowed_actions:
            self._errors.append(
                f"ON DELETE action of '{self.on_delete}' for constraint {self.name} is not a valid ON DELETE action"
            )

        if self.on_update not in allowed_actions:
            self._errors.append(
                f"ON UPDATE action of '{self.on_update}' for constraint {self.name} is not a valid ON UPDATE action"
            )

    def __str__(self) -> str:
        """ Returns the MySQL command that would create the constraint

        i.e. CONSTRAINT `vendors_w9_fk` FOREIGN KEY (`w9_id`) REFERENCES `vendor_w9s` (`id`) ON UPDATE CASCADE
        """
        return ' '.join([
            'CONSTRAINT',
            f'`{self.name}`',
            'FOREIGN KEY',
            f'(`{self.column_name}`)',
            'REFERENCES',
            f'`{self.foreign_table}`',
            f'(`{self.foreign_column_name}`)',
            f'ON DELETE {self.on_delete}',
            f'ON UPDATE {self.on_update}',
        ])
