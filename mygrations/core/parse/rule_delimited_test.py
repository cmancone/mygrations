import unittest

from mygrations.core.parse.rule_delimited import RuleDelimited
class RuleDelimitedTest(unittest.TestCase):
    def get_rule(self, name, separator, quote, literal):

        return RuleDelimited(
            False, {
                'name': name,
                'separator': separator,
                'quote': quote
            }, {
                'type': 'literal',
                'value': literal
            }
        )

    def test_name_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('', ',', '`', 'asdf')

    def test_separator_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('bob', '', '', 'asdf')

    def test_no_multi_character_separator(self):

        with self.assertRaises(ValueError):

            self.get_rule('bob', 'as', '', 'asdf')

    def test_no_multi_character_quote(self):

        with self.assertRaises(ValueError):

            self.get_rule('bob', ',', 'as', 'asdf')

    def test_literal_required(self):

        with self.assertRaises(ValueError):

            RuleDelimited(False, {'name': 'bob', 'separator': ',', 'quote': '`'}, {})

    def test_can_init_with_name_and_separator(self):

        rule = self.get_rule('bob', ',', '', 'asdf')
        self.assertEquals(rule.name, 'bob')
        self.assertEquals(rule.separator, ',')

    def test_parse_without_quote(self):

        rule = self.get_rule('bob', ',', '', ')')
        self.assertTrue(rule.parse('1,2,3,4)'))
        self.assertEquals(['1', '2', '3', '4'], rule.result)
        self.assertEquals(')', rule.leftovers)

    def test_parse_optional_quotes(self):

        rule = self.get_rule('bob', ',', '`', ')')
        self.assertTrue(rule.parse('asdf,`bob`,huh,`okay`) sup'))
        self.assertEquals(['asdf', 'bob', 'huh', 'okay'], rule.result)
        self.assertEquals(') sup', rule.leftovers)

    def test_syntax_error_missing_quote(self):

        with self.assertRaises(SyntaxError):

            rule = self.get_rule('bob', ',', '`', ')')
            rule.parse('asdf,`bob)')

    def test_separator_in_quotes(self):

        rule = self.get_rule('bob', ',', '`', ')')
        self.assertTrue(rule.parse('asdf,`bob,`,huh,`okay`) sup'))
        self.assertEquals(['asdf', 'bob,', 'huh', 'okay'], rule.result)
        self.assertEquals(') sup', rule.leftovers)

    def test_alternate_characters(self):

        rule = self.get_rule('bob', 'X', '<', 'asdf')

        self.assertTrue(rule.parse('<hey<X<sup<asdf'))
        self.assertEquals(['hey', 'sup'], rule.result)
        self.assertEquals('asdf', rule.leftovers)
