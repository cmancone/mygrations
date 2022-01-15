from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, List, Tuple
from .base import Base
class Constraint(Base):
    _column_name: str = ''
    _errors: List[str] = None
    _foreign_table_name: str = ''
    _foreign_column_name: str = ''
    _name: str = ''
    _on_delete: str = ''
    _on_update: str = ''
    _warnings: List[str] = None

    def __init__(
        self,
        name: str = '',
        column_name: str = '',
        foreign_table_name: str = '',
        foreign_column_name: str = '',
        on_delete: str = '',
        on_update: str = ''
    ):
        self._column_name = column_name
        self._foreign_table_name = foreign_table_name
        self._foreign_column_name = foreign_column_name
        self._name = name
        self._on_delete = on_delete.upper()
        self._on_update = on_update.upper()
        if not self._on_delete:
            self._on_delete = 'RESTRICT'
        if not self._on_update:
            self._on_update = 'RESTRICT'
        self._schema_errors = None
        self._schema_warnings = None
        self._parsing_errors = None
        self._parsing_warnings = None

    @property
    def name(self) -> str:
        """ Public getter.  Returns the name of the constraint. """
        return self._name

    @property
    def column_name(self) -> str:
        """ Public getter.  Returns the name of the column this constraint is on """
        return self._column_name

    @property
    def foreign_table_name(self) -> str:
        """ Public getter.  Returns the name of the table this constraint is to """
        return self._foreign_table_name

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

    def _check_for_schema_errors_and_warnings(self) -> List[str]:
        self._schema_errors = []
        self._schema_warnings = []

        allowed_actions = ['CASCADE', 'NO ACTION', 'RESTRICT', 'SET DEFAULT', 'SET NULL']
        if not self.name:
            self._schema_errors.append('Missing name for constraint')
        elif len(self._name) > 64:
            self._schema_errors.append(f"Key name '{self.name}' is too long")

        if self.on_delete not in allowed_actions:
            self._schema_errors.append(
                f"ON DELETE action of '{self.on_delete}' for constraint '{self.name}' is not a valid ON DELETE action"
            )

        if self.on_update not in allowed_actions:
            self._schema_errors.append(
                f"ON UPDATE action of '{self.on_update}' for constraint '{self.name}' is not a valid ON UPDATE action"
            )

        for required in ['name', 'column_name', 'foreign_table_name', 'foreign_column_name']:
            if not getattr(self, required):
                self._schema_errors.append(f"Missing {required} for constraint '{self.name}'")

    def __str__(self) -> str:
        """ Returns the MySQL command that would create the constraint

        i.e. CONSTRAINT `vendors_w9_fk` FOREIGN KEY (`w9_id`) REFERENCES `vendor_w9s` (`id`) ON UPDATE CASCADE

        :returns: A partial MySQL command that could be used to generate the foreign key
        :rtype: string
        """
        return ' '.join([
            'CONSTRAINT',
            f'`{self.name}`',
            'FOREIGN KEY',
            f'(`{self.column_name}`)',
            'REFERENCES',
            f'`{self.foreign_table_name}`',
            f'(`{self.foreign_column_name}`)',
            f'ON DELETE {self.on_delete}',
            f'ON UPDATE {self.on_update}',
        ])
