from .rule_base import RuleBase
import re
class RuleRegexp(RuleBase):
    """ rule = rule_regexp( parser, rule, next_rule )

    rule_literal constructor.  Pass in the parser object that the rule is for, the rule
    that is being parsed, and the next rule in the parsing chain.

    This class attempts to match a regular expression (case-insensitive).

    keys for the rules dictionary:

    =========  ========
    key        contents
    =========  ========
    value      The regular expression to look for
    name       The name of the rule
    optional   (optional) If true, denotes that this rule is optional
    =========  ========

    :param parser: The parser that this rule belongs to
    :param rule: A dictionary representing the rule configuration (see each rule class for details)
    :param next_rule: A dictionary representing the next rule
    :type parser: parser
    :type rule: dict
    :type next_rule: dict
    :returns: rule object
    """

    regexp = ''

    def __init__(self, parser, rule, next_rule):

        super().__init__(parser, rule, next_rule)

        self.regexp = self.rule['value']

    def parse(self, string):

        # apply the regular expression!
        result = re.match(self.regexp, string, re.IGNORECASE)

        # if it didn't match then nothing channged
        if not result:
            self.leftovers = string
            self.result = ''
            return False

        # otherwise we have a match and can return as such
        self.result = result.group(0)
        cleaned = string[len(self.result):].strip()

        # if there was a group in the regular expression then just keep that part
        if result.groups():
            self.result = result.group(1)

        self.leftovers = cleaned
        return True
