import unittest
from .enable_checks import EnableChecks
class EnableChecksTest(unittest.TestCase):
    def test_as_string(self):
        self.assertEquals("SET FOREIGN_KEY_CHECKS=1;", str(EnableChecks()))
