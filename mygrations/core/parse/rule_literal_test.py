import unittest

from mygrations.core.parse.rule_literal import RuleLiteral
class RuleLiteralTest(unittest.TestCase):
    def get_rule(self, name, literal):

        return RuleLiteral(False, {'name': name, 'value': literal}, {})

    def test_name_not_required(self):

        rule = self.get_rule('', 'ASDF')
        self.assertEquals(rule.name, 'ASDF')

    def test_value_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('bob', '')

    def test_can_init_with_name_and_value(self):

        rule = self.get_rule('bob', ',')
        self.assertEquals(rule.name, 'bob')
        self.assertEquals(rule.literal, ',')

    def test_match_beginning_only(self):

        rule = self.get_rule('bob', ',')
        self.assertFalse(rule.parse('hey,'))
        self.assertEquals('', rule.result)

    def test_leftovers_is_input_for_no_match(self):

        rule = self.get_rule('bob', ',')
        string = 'hey,'
        rule.parse(string)

        self.assertEquals(string, rule.leftovers)

    def test_no_leftovers_for_full_match(self):

        string = '23483438'
        rule = self.get_rule('bob', string)

        self.assertTrue(rule.parse(string))
        self.assertEquals(string, rule.result)
        self.assertEquals('', rule.leftovers)

    def test_calc_leftovers_trim(self):

        rule = self.get_rule('bob', ',')

        string = ', bob'

        self.assertTrue(rule.parse(string))
        self.assertEquals(',', rule.result)
        self.assertEquals('bob', rule.leftovers)
