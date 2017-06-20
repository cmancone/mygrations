import unittest

from mygrations.core.parse.rule_children import rule_children
from mygrations.core.parse.parser import parser

class test_rule( parser ):

    rules = [
        { 'type': 'literal', 'value': 'bob' },
        { 'type': 'literal', 'value': 'greg' }
    ]

class test_rule_two( parser ):

    rules = [
        { 'type': 'regexp', 'name': 'test_regexp', 'value': '\d+' },
        { 'type': 'literal', 'value': 'sup' }
    ]

class test_parse_children( unittest.TestCase ):

    def get_rule( self, name, classes ):

        return rule_children( False, { 'name': name, 'classes': classes }, {} )

    def test_name_required( self ):

        with self.assertRaises( ValueError ):

            self.get_rule( '', [ test_rule ] )

    def test_classes_required( self ):

        with self.assertRaises( ValueError ):

            self.get_rule( 'bob', [] )

    # if nothing matches at the start then we get no match
    def test_match_start_only( self ):

        rule = self.get_rule( 'test', [ test_rule, test_rule_two ] )
        self.assertFalse( rule.parse( 'okay bob greg' ) )
        self.assertEquals( '', rule.result )
        self.assertEquals( 'okay bob greg', rule.leftovers )
