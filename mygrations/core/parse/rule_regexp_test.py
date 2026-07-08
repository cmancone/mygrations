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

        rule = self.get_rule('bob', r'\S+')
        self.assertEqual(rule.name, 'bob')
        self.assertEqual(rule.regexp, r'\S+')

    def test_match_beginning_only(self):

        rule = self.get_rule('bob', r'\d+')
        self.assertFalse(rule.parse('hey 123'))
        self.assertEqual('', rule.result)

    def test_leftovers_is_input_for_no_match(self):

        rule = self.get_rule('bob', r'\d+')
        string = 'hey 123'
        rule.parse(string)

        self.assertEqual(string, rule.leftovers)

    def test_no_leftovers_for_full_match(self):

        rule = self.get_rule('bob', r'\d+')
        string = '23483438'

        self.assertTrue(rule.parse(string))
        self.assertEqual(string, rule.result)
        self.assertEqual('', rule.leftovers)

    def test_return_group_only(self):

        rule = self.get_rule('bob', r'\d+\s+(\w+)')

        string = '999 bob'

        self.assertTrue(rule.parse(string))
        self.assertEqual('bob', rule.result)
        self.assertEqual('', rule.leftovers)

    def test_calc_leftovers_trim(self):

        rule = self.get_rule('bob', r'\d+')

        string = '999 bob'

        self.assertTrue(rule.parse(string))
        self.assertEqual('999', rule.result)
        self.assertEqual('bob', rule.leftovers)
