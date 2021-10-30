from mygrations.core.definitions.constraint import Constraint as BaseConstraint

class Constraint(BaseConstraint):
    def __init__(self, name='', column_name='', foreign_table_name='', foreign_column_name='', on_delete='', on_update=''):
        super().__init__(
            name=name,
            column_name=column_name,
            foreign_table_name=foreign_table_name,
            foreign_column_name=foreign_column_name,
            on_delete=on_delete,
            on_update=on_update
        )

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
            f'`{self.foreign_table}`',
            f'(`{self.foreign_column_name}`)',
            f'ON DELETE {self.on_delete}',
            f'ON UPDATE {self.on_update}',
        ])
