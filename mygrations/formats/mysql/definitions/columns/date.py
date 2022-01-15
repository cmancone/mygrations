from mygrations.core.definitions.columns.date import Date as DateBase
from typing import List, Union
class Date(DateBase):
    def __init__(
        self,
        name: str = '',
        column_type: str = '',
        length: Union[str, int] = None,
        null: bool = True,
        has_default: bool = False,
        default: Union[str, int] = None,
        unsigned: bool = None,
        character_set: str = None,
        collate: str = None,
        auto_increment: bool = False,
        enum_values: List[str] = None,
        parsing_errors: List[str] = None,
        parsing_warnings: List[str] = None,
    ):
        # it would be nice to just do `def __init__(**kwargs)` and then `super().__init__(**kwargs)`
        # but then we would lose our type hints.  :shrug:
        super().__init__(
            name=name,
            column_type=column_type,
            length=length,
            null=null,
            has_default=has_default,
            default=default,
            character_set=character_set,
            collate=collate,
            auto_increment=auto_increment,
            enum_values=enum_values,
            parsing_errors=parsing_errors,
            parsing_warnings=parsing_warnings,
            unsigned=unsigned,
        )
