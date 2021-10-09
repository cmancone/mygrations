from .column import Column
class Date(Column):
    _allowed_column_types = [
        'DATE',
        'DATETIME',
        'TIMESTAMP',
    ]
