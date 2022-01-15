class RuleBase:
    """ rule = rule_base( parser, rule, next_rule )

    Base class for rule parsers: the smallest part of our rule based parsing.  Each rule parser
    (currently rule_children, rule_delimited, rule_literal, and rule_regexp) specifies a different
    *kind* of rule to match against while parsing SQL.  Quick summary:

    ================  =======================
    Class             Description
    ================  =======================
    rule_children     Matches any number of parsers against the string
    rule_delimited    Finds delimited text values
    rule_literal      Finds literal text values
    rule_regexp       Matches a regular expression against the string
    ================  =======================

    """

    require_name = True
    require_value = True
    require_next = False

    parser_class = ''
    rule = {}
    next_rule = {}
    name = ''
    result = ''
    leftovers = ''

    def __init__(self, parser, rule, next_rule):
        """ rule = rule_base( parser, rule, next_rule )

        rule constructor.  Pass in the parser object that the rule is for, the rule
        that is being parsed, and the next rule in the parsing chain.

        rules only match at the very beginning of the string being matched.

        :param parser: The parser that this rule belongs to
        :param rule: A dictionary representing the rule configuration (see each rule class for details)
        :param next_rule: A dictionary representing the next rule
        :type parser: parser
        :type rule: dict
        :type next_rule: dict
        :returns: rule object
        """

        # we keep parser class around just for reference and better errors
        self.parser_class = parser.__class__

        # store rule and next_rule
        self.rule = rule
        self.next_rule = next_rule

        self.name = self.rule['name'] if 'name' in self.rule else ''

        # name is requied more often than not
        if self.require_name and not self.name:
            raise ValueError("name required for rule %s in class %s" % (self.rule, self.parser_class))

        # ditto rule
        if self.require_value:
            if not 'value' in self.rule or not self.rule['value']:
                raise ValueError('missing value in rule %s for class %s' % (self.rule, self.parser_class))

    def parse(self, string):
        """ rule.parse( string )

        Parse the string according to the rule class and configuration.  Returns True/False to denote
        a match, and populates self.result and self.leftovers accordingly.

        :param string: The string to parse
        :type string: str
        :returns: boolean
        """

        # why is this here?  Because python abstract classes are stange, and I don't feel like bothering with them.
        # this accomplishes the exact same thing, just at run-time instead of compile-time.  Not a big deal
        # in this case.
        raise ValueError("You forgot to extend rule_base.parse")
