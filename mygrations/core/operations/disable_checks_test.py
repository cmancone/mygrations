import unittest
from .disable_checks import DisableChecks
class DisableChecksTest(unittest.TestCase):
    def test_as_string(self):
        self.assertEquals("SET FOREIGN_KEY_CHECKS=0;", str(DisableChecks()))
