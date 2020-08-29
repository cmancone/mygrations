class Option:
    _name: str = ''
    _value: str = ''

    def __init__(self, name: str, value: str):
        self._name = name
        self._value = value

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
