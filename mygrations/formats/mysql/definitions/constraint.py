from mygrations.core.definitions.constraint import Constraint as BaseConstraint
class Constraint(BaseConstraint):
    def __init__(
        self, name='', column_name='', foreign_table_name='', foreign_column_name='', on_delete='', on_update=''
    ):
        super().__init__(
            name=name,
            column_name=column_name,
            foreign_table_name=foreign_table_name,
            foreign_column_name=foreign_column_name,
            on_delete=on_delete,
            on_update=on_update
        )
