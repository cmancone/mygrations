from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, List


class Constraint(object):
    _name: str = ''
    _column: str = ''
    _foreign_table: str = ''
    _foreign_column: str = ''
    _on_delete: str = ''
    _on_update: str = ''
    _errors: List[str] = None
    _warnings: List[str] = None

    def __init__(
        self,
        column: str = '',
        name: str = '',
        foreign_table: str = '',
        foreign_column: str = '',
        on_delete: str = '',
        on_update: str = ''
    ):
        self._column = column
        self._errors = []
        self._foreign_table = foreign_table
        self._foreign_column = foreign_column
        self._name = name
        self._on_delete = on_delete
        self._on_update = on_update
        self._warnings = []

    @property
    def name(self) -> str:
        """ Public getter.  Returns the name of the column.

        :returns: The index name
        """
        return self._name

    @property
    def column(self) -> str:
        """ Public getter.  Returns the name of the column this constraint is on

        :returns: The column name
        """
        return self._column

    @property
    def foreign_table(self) -> str:
        """ Public getter.  Returns the name of the table this constraint is to

        :returns: The foreign table name
        """
        return self._foreign_table

    @property
    def foreign_column(self) -> str:
        """ Public getter.  Returns the name of the column in the foreign table this constraint is to

        :returns: The foreign column name
        """
        return self._foreign_column

    @property
    def on_delete(self) -> str:
        """ Public getter.  Returns the ON DELETE action for this constraint

        :returns: The ON DELETE action
        """
        return self._on_delete

    @property
    def on_update(self) -> str:
        """ Public getter.  Returns the ON UPDATE action for this constraint

        :returns: The ON UPDATE action
        """
        return self._on_update

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
            f'(`{self.column}`)',
            'REFERENCES',
            f'`{self.foreign_table}`',
            f'(`{self.foreign_column}`)',
            f'ON DELETE {self.on_delete}',
            f'ON UPDATE {self.on_update}',
        ])
