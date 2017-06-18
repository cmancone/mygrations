from .rule_base import rule_base

class rule_literal( rule_base ):

    # names are not required for literals
    require_name = False

    literal = ''

    def __init__( self, parser, rule, next_rule ):

        super().__init__( parser, rule, next_rule )

        self.literal = self.rule['value']

        # use the actual literal value as the name if we don't have one
        if not self.name:
            self.name = self.literal

    def parse( self, string ):

        # easy to check for a literal match at the beginning of string
        val_len = len( self.literal )
        if string[:val_len].lower() != self.literal.lower():
            self.result = ''
            self.leftovers = string
            return False

        # if we matched then clean!
        self.leftovers = string[val_len:].strip()
        self.result = self.literal
        return True
