import unittest
from .option import Option
class TestOption(unittest.TestCase):
    def test_can_create(self):
        option = Option('my_option', 'my_value')

        self.assertEquals('my_option', option.name)
        self.assertEquals('my_value', option.value)
