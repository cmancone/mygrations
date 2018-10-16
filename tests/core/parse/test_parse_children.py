import unittest

from mygrations.core.parse.rule_children import rule_children
from mygrations.core.parse.parser import parser
class test_rule(parser):

    rules = [{'type': 'literal', 'value': 'bob'}, {'type': 'literal', 'value': 'greg'}]
class test_rule_two(parser):

    rules = [{'type': 'regexp', 'name': 'test_regexp', 'value': '\d+'}, {'type': 'literal', 'value': 'sup'}]
class test_rule_overlap(parser):

    rules = [{'type': 'regexp', 'name': 'test_overlap', 'value': '\S+'}]
class test_parse_children(unittest.TestCase):
    def get_rule(self, name, classes):

        return rule_children(False, {'name': name, 'classes': classes}, {})

    def test_name_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('', [test_rule])

    def test_classes_required(self):

        with self.assertRaises(ValueError):

            self.get_rule('bob', [])

    # if nothing matches at the start then we get no match
    def test_match_start_only(self):

        rule = self.get_rule('test', [test_rule, test_rule_two])
        self.assertFalse(rule.parse('okay bob greg'))
        self.assertEquals('', rule.result)
        self.assertEquals('okay bob greg', rule.leftovers)

    # we should be able to match any number of children in any order
    # as long as their parsers match, we will match them
    def test_match_any_order(self):

        rule = self.get_rule('test', [test_rule, test_rule_two])
        self.assertTrue(rule.parse('999 sup bob greg bob greg 1234568 sup hey'))
        self.assertEquals('hey', rule.leftovers)

        self.assertEquals(4, len(rule.result))
        self.assertTrue(rule.result[0].__class__ == test_rule_two)
        self.assertTrue(rule.result[1].__class__ == test_rule)
        self.assertTrue(rule.result[2].__class__ == test_rule)
        self.assertTrue(rule.result[3].__class__ == test_rule_two)

    # if two rules both match a string the rule that matches
    # the largest portion of the string wins.
    def test_matches_most_wins(self):

        rule = self.get_rule('test', [test_rule_overlap, test_rule])

        self.assertTrue(rule.parse('bob greg'))
        self.assertTrue(rule.result[0].__class__ == test_rule)
        self.assertEquals('', rule.leftovers)

    # if a child can't match all required params other
    # children can match
    def test_missing_required_cant_match(self):

        rule = self.get_rule('test', [test_rule_overlap, test_rule])

        self.assertTrue(rule.parse('bob'))
        self.assertTrue(rule.result[0].__class__ == test_rule_overlap)
        self.assertEquals('', rule.leftovers)
