from typing import Union, List
class Option:
    _name: str = ''
    _value: str = ''
    _schema_errors: List[str] = None
    _schema_warnings: List[str] = None
    _parsing_errors: List[str] = None
    _parsing_warnings: List[str] = None

    def __init__(self, name: str = '', value: str = ''):
        self._name = name
        self._value = value
        self._schema_errors = None
        self._schema_warnings = None
        self._parsing_errors = None
        self._parsing_warnings = None

    @property
    def name(self) -> str:
        """ Public getter.  Returns the name of the option.

        :returns: The option name
        """
        return self._name

    @property
    def value(self) -> str:
        """ Public getter.  Returns the value of the option.

        :returns: The option value
        """
        return self._value

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

    def _check_for_schema_errors_and_warnings(self):
        self._schema_errors = []
        self._schema_warnings = []
        for required in ['name', 'value']:
            if not getattr(self, required):
                self._schema_errors.append(f"Missing {required} for option {self.name}")
        if len(self.name) > 64:
            self._schema_errors.append('Option name %s must be <=64 characters long' % (self._name))
