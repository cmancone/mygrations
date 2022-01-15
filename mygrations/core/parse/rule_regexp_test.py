import unittest

from mygrations.core.parse.rule_regexp import RuleRegexp
class RuleRegexpTest(unittest.TestCase):
    def get_rule(self, name, regexp):

        return RuleRegexp(False, {'name': name, 'value': regexp}, {})

    def test_name_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('', '')

    def test_value_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('bob', '')

    def test_can_init_with_name_and_value(self):

        rule = self.get_rule('bob', '\S+')
        self.assertEquals(rule.name, 'bob')
        self.assertEquals(rule.regexp, '\S+')

    def test_match_beginning_only(self):

        rule = self.get_rule('bob', '\d+')
        self.assertFalse(rule.parse('hey 123'))
        self.assertEquals('', rule.result)

    def test_leftovers_is_input_for_no_match(self):

        rule = self.get_rule('bob', '\d+')
        string = 'hey 123'
        rule.parse(string)

        self.assertEquals(string, rule.leftovers)

    def test_no_leftovers_for_full_match(self):

        rule = self.get_rule('bob', '\d+')
        string = '23483438'

        self.assertTrue(rule.parse(string))
        self.assertEquals(string, rule.result)
        self.assertEquals('', rule.leftovers)

    def test_return_group_only(self):

        rule = self.get_rule('bob', '\d+\s+(\w+)')

        string = '999 bob'

        self.assertTrue(rule.parse(string))
        self.assertEquals('bob', rule.result)
        self.assertEquals('', rule.leftovers)

    def test_calc_leftovers_trim(self):

        rule = self.get_rule('bob', '\d+')

        string = '999 bob'

        self.assertTrue(rule.parse(string))
        self.assertEquals('999', rule.result)
        self.assertEquals('bob', rule.leftovers)
