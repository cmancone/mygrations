import unittest
from mygrations.core.parse.rule_children import RuleChildren
from mygrations.core.parse.parser import Parser
class TestRule(Parser):

    rules = [{'type': 'literal', 'value': 'bob'}, {'type': 'literal', 'value': 'greg'}]
class TestRuleTwo(Parser):

    rules = [{'type': 'regexp', 'name': 'test_regexp', 'value': '\d+'}, {'type': 'literal', 'value': 'sup'}]
class TestRuleOverlap(Parser):

    rules = [{'type': 'regexp', 'name': 'test_overlap', 'value': '\S+'}]
class RuleChildrenTest(unittest.TestCase):
    def get_rule(self, name, classes):

        return RuleChildren(False, {'name': name, 'classes': classes}, {})

    def test_name_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('', [TestRule])

    def test_classes_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('bob', [])

    # if nothing matches at the start then we get no match
    def test_match_start_only(self):

        rule = self.get_rule('test', [TestRule, TestRuleTwo])
        self.assertFalse(rule.parse('okay bob greg'))
        self.assertEquals('', rule.result)
        self.assertEquals('okay bob greg', rule.leftovers)

    # we should be able to match any number of children in any order
    # as long as their parsers match, we will match them
    def test_match_any_order(self):

        rule = self.get_rule('test', [TestRule, TestRuleTwo])
        self.assertTrue(rule.parse('999 sup bob greg bob greg 1234568 sup hey'))
        self.assertEquals('hey', rule.leftovers)

        self.assertEquals(4, len(rule.result))
        self.assertTrue(rule.result[0].__class__ == TestRuleTwo)
        self.assertTrue(rule.result[1].__class__ == TestRule)
        self.assertTrue(rule.result[2].__class__ == TestRule)
        self.assertTrue(rule.result[3].__class__ == TestRuleTwo)

    # if two rules both match a string the rule that matches
    # the largest portion of the string wins.
    def test_matches_most_wins(self):

        rule = self.get_rule('test', [TestRuleOverlap, TestRule])

        self.assertTrue(rule.parse('bob greg'))
        self.assertTrue(rule.result[0].__class__ == TestRule)
        self.assertEquals('', rule.leftovers)

    # if a child can't match all required params other
    # children can match
    def test_missing_required_cant_match(self):

        rule = self.get_rule('test', [TestRuleOverlap, TestRule])

        self.assertTrue(rule.parse('bob'))
        self.assertTrue(rule.result[0].__class__ == TestRuleOverlap)
        self.assertEquals('', rule.leftovers)
