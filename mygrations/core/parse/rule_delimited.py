from .rule_base import rule_base

class rule_delimited( rule_base ):

    require_value = False

    separator = ''
    quote = ''

    def __init__( self, parser, rule, next_rule ):

        super().__init__( parser, rule, next_rule )

        if not 'separator' in rule or not rule['separator']:
            raise ValueError( 'Missing separator for rule %s' % rule )

        # assumption: delimiteds are always followed up by a literal
        if not self.next_rule or self.next_rule['type'] != 'literal':
            raise ValueError( "Delimited rules must be followed by a literal for rule %s in class %s, next: %s" % ( self.rule, self.parser_class, self.next_rule ) )

        if not 'value' in self.next_rule or not self.next_rule['value']:
            raise ValueError( "Delimited rules must be followed by a literal rule with a value for rule %s in class %s, next: %s" % ( self.rule, self.parser_class, self.next_rule ) )

        self.separator = self.rule['separator']
        self.quote = self.rule['quote'] if 'quote' in self.rule else ''


    def parse( self, string ):

        end = self.next_rule['value'].lower()
        end_len = len( end )

        # it's ugly, but we will do this one character at a time
        has_word = False
        vals = []
        current = ''
        in_quote = False
        for ( index, char ) in enumerate( string ):

            # if we hit a quote then we need to start/finish a word
            if self.quote and char == self.quote:

                # open word
                if not in_quote:
                    in_quote = True
                    has_word = True
                    current = ''

                # close word
                else:
                    vals.append( current )
                    has_word = False
                    in_quote = False

                continue

            # next deal with other characters outside of quotes
            if not in_quote:

                # are we done parsing?

                if string[index:index+end_len].lower() == end:
                    if has_word:
                        vals.append( current )
                    break

                # if we hit a separator then we need to start a new word
                if char == self.separator:

                    if has_word:
                        vals.append( current )
                        has_word = False
                    current = ''

                    continue

                # skip white space outside of quotes (also end a word)
                if char == ' ':
                    if has_word:
                        vals.append( current )
                        has_word = False

                    current = ''
                    continue

                # otherwise we have a character for a word
                has_word = True
                current += char
                continue

            # If we get here then we are inside a quote and the character
            # we are working with is not a quote.  This is easy.
            current += char

        # We are out of our processing loop!
        # if we are still in quote then there was a syntax error in the SQL
        if in_quote:
            raise SyntaxError( "Opening quote without closing quote at %s" % string )

        # did we match anything?
        if not vals:
            self.leftovers = string
            self.result = ''
            return False

        # almost done: one last step.  Remove everything that we parsed from string.
        # we know what index we stopped at, so it is easy.
        self.leftovers = string[index:]
        self.result = vals
        return True
