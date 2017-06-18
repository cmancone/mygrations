from .rule_base import rule_base
import re

class rule_regexp( rule_base ):

    regexp = ''

    def __init__( self, parser, rule, next_rule ):

        super().__init__( parser, rule, next_rule )

        self.regexp = self.rule['value']

    def parse( self, string ):

        # apply the regular expression!
        result = re.match( self.regexp, string, re.IGNORECASE )

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
