from .rule_base import RuleBase
class RuleLiteral(RuleBase):
    """ rule = rule_children( parser, rule, next_rule )

    rule_literal constructor.  Pass in the parser object that the rule is for, the rule
    that is being parsed, and the next rule in the parsing chain.

    This class attempts to match a literal string (case-insensitive).

    keys for the rules dictionary:

    =========  ========
    key        contents
    =========  ========
    value      The literal value to look for
    name       (optional) The name of the rule
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

    # names are not required for literals
    require_name = False

    literal = ''

    def __init__(self, parser, rule, next_rule):

        super().__init__(parser, rule, next_rule)

        self.literal = self.rule['value']

        # use the actual literal value as the name if we don't have one
        if not self.name:
            self.name = self.literal

    def parse(self, string):

        # easy to check for a literal match at the beginning of string
        val_len = len(self.literal)
        if string[:val_len].lower() != self.literal.lower():
            self.result = ''
            self.leftovers = string
            return False

        # if we matched then clean!
        self.leftovers = string[val_len:].strip()
        self.result = self.literal
        return True
