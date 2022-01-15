import re
from .rule_children import RuleChildren
from .rule_delimited import RuleDelimited
from .rule_literal import RuleLiteral
from .rule_regexp import RuleRegexp
class Parser:
    rule_types = {'children': RuleChildren, 'delimited': RuleDelimited, 'literal': RuleLiteral, 'regexp': RuleRegexp}
    _parsing_errors = None
    _parsing_warnings = None
    _values = None

    @property
    def parsing_errors(self):
        """ Public getter.  Returns a list of parsing errors

        :returns: A list of parsing errors
        :rtype: list
        """
        return self._parsing_errors if self._parsing_errors is not None else []

    @property
    def parsing_warnings(self):
        """ Public getter.  Returns a list of parsing warnings

        :returns: A list of parsing warnings
        :rtype: list
        """
        return self._parsing_warnings if self._parsing_warnings is not None else []

    def __getitem__(self, key):

        return self._values[key]

    def __len__(self):

        return len(self._values)

    def has_key(self, key):

        return key in self._values

    def keys(self):

        return self._values.keys()

    def values(self):

        return self._values.values()

    def items(self):

        return self._values.items()

    def get_rule_parser(self, rule, next_rule):

        rule_type = rule['type']

        # keeping this simple for now
        if not rule_type in self.rule_types:
            raise ValueError('Unknown rule type %s for class %s' % (rule_type, self.__class__))

        return self.rule_types[rule_type](self, rule, next_rule)

    def parse(self, string=''):

        # first thing first, some initial string cleaning.  Clean spaces
        # from start and end and replace any multi-spaces with a single space.
        string = re.sub('\s+', ' ', string).strip()
        number_rules = len(self.rules)
        self._values = {}

        for (rule_index, rule) in enumerate(self.rules):

            # do we have a next rule?
            next_rule = self.rules[rule_index + 1] if rule_index < number_rules - 1 else False

            # now we can parse
            rule_parser = self.get_rule_parser(rule, next_rule)

            # does it match?  Check for a lack of match and deal with that first
            if not rule_parser.parse(string):

                # if this rule wasn't optional then we just don't match
                if not 'optional' in rule or not rule['optional']:
                    self.matched = False
                    return string

                # otherwise just keep going
                continue

            # we did match!  Yeah!
            self._values[rule_parser.name] = rule_parser.result
            string = rule_parser.leftovers

            # we are all done if we have nothing left
            if not string:
                break

        # if we got here then we got to the end, but we may not be done.  If we have more required
        # rules left that haven't been matched, then we don't match.

        # did we check every required rule?
        for check_index in range(rule_index + 1, number_rules):
            rule = self.rules[check_index]
            if not 'optional' in rule or not rule['optional']:
                self.matched = False
                return string

        # if we got here then we didn't match everything, but we fulfilled all of our
        # required rules.  As a result, we are done!
        self.process()
        self.matched = True
        return string

    def process(self):
        """ parser.process()

        Processes the results of the parsing process.  Only called if a match is found.  No input
        or output as it modifies the parser object in place, populating attributes as needed.
        """

        pass
