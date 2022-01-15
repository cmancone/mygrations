from .rule_base import RuleBase
class RuleChildren(RuleBase):
    """ rule = rule_children( parser, rule, next_rule )

    rule_children constructor.  Pass in the parser object that the rule is for, the rule
    that is being parsed, and the next rule in the parsing chain.

    This class takes as input a list of parser classes to be matched against the string
    being parsed.  During parsing, it will attempt to fit any of the child parsers (in
    any order) against the string being parsed.  After each match, the matched contents
    will be removed and parsing will start again.  This repeats until no more matches
    can be found.

    keys for the rules dictionary:

    =========  ========
    key        contents
    =========  ========
    name       The name of the rule
    classes    A list with classes to be matched
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

    require_value = False

    classes = []

    def __init__(self, parser, rule, next_rule):

        super().__init__(parser, rule, next_rule)

        if not 'classes' in self.rule:
            raise ValueError('Missing classes for children rule %s in %s' % (rule, self.parser_class))

        if not self.rule['classes']:
            raise ValueError('Missing classes for children rule %s in %s' % (rule, self.parser_class))

        self.classes = self.rule['classes']

    def parse(self, string):

        matches = []

        # we need to keep looping through the children looking for matches
        # to the string until we no longer get any matches.  Then return.
        c = 0
        while string:

            c += 1
            if c > 1000:
                raise ValueError('Max depth reached')

            shortest_leftover = False
            best_match = False
            best_leftover = ''
            current_string = string

            for child in self.classes:

                # let the child parse the string
                child_parser = child()
                leftover = child_parser.parse(current_string)

                # if it didn't do anything then this child didn't match
                if not child_parser.matched:
                    continue

                # It is possible that more than one child matches.  If so,
                # prioritize the child that matches the largest part of the
                # string.  All else being equal, first come first serve
                if best_match:
                    if len(leftover) < shortest_leftover:
                        shortest_leftover = len(leftover)
                        best_match = child_parser
                        best_leftover = leftover
                else:
                    shortest_leftover = len(leftover)
                    best_match = child_parser
                    best_leftover = leftover

            # we have a match!
            if best_match:
                string = best_leftover
                matches.append(best_match)

            # If we didn't find anything then we are completely done
            else:
                if matches:
                    self.leftovers = string
                    self.result = matches
                    return True
                else:
                    self.leftovers = string
                    self.result = ''
                return False

        # the only way we would get here is if we matched the entire string
        self.leftovers = ''
        self.result = matches
        return True
