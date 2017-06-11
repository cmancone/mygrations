import re

class parser( object ):

    num_rules = 0;
    rules = []

    _values = {}
    matched = False

    def __init__( self, rules = [] ):

        self._values = {}

        # rules should be defined by the subclass
        if rules:
            self.rules = rules

        if not self.rules:
            raise ValueError( "Cannot extend parser without providing rules in %s" % ( self.__class__ ) )

        self.num_rules = len( self.rules )

    def __getitem__( self, key ):

        return self._values[key]

    def __len__( self ):

        return len( self._values )

    def has_key( self, key ):

        return key in self._values

    def keys( self ):

        return self._values.keys()

    def values( self ):

        return self._values.values()

    def items( self ):

        return self._values.items()

    def parse( self, string = '' ):

        # first thing first, some initial string cleaning.  Clean spaces
        # from start and end and replace any multi-spaces with a single space.
        string = re.sub( '\s+', ' ', string ).strip()

        for ( rule_index, rule ) in enumerate( self.rules ):

            # we always need a type
            if not 'type' in rule:
                raise ValueError( 'Missing type for rule %s in %s' % ( rule, self.__class__ ) )

            # we need a name for every rule but literal
            if not 'name' in rule and rule['type'] != 'literal':
                raise ValueError( 'Missing name for rule %s in %s' % ( rule, self.__class__ ) )

            # do we have a next rule?
            next_rule = self.rules[rule_index+1] if rule_index < self.num_rules-1 else False

            # now we can parse
            if rule['type'] == 'regexp':

                ( string, data ) = self.process_regexp( string, rule, next_rule )

                name = rule['name']

            elif rule['type'] == 'literal':

                ( string, data ) = self.process_literal( string, rule, next_rule )

                name = rule['name'] if 'name' in rule else rule['value']

            elif rule['type'] == 'children':

                ( string, data ) = self.process_children( string, rule, next_rule )

                name = rule['name']

            elif rule['type'] == 'delimited':

                ( string, data ) = self.process_delimited( string, rule, next_rule )

                name = rule['name']

            else:

                raise ValueError( 'Unknown rule type: %s for rule %s in %s' % ( rule['type'], rule, self.__class__ ) )

            # did we match???
            if data:
                self._values[name] = data

            # if we didn't, and we weren't optional, then the parser
            # doesn't match at all
            elif not 'optional' in rule or not rule['optional']:
                self.matched = False
                return string

            if not string:
                break

        # if we got here then we got to the end, but we may not be done.  If we have more required
        # rules left that haven't been matched, then we don't match.

        # did we check every required rule?
        for check_index in range( rule_index+1, self.num_rules ):
            if not 'optional' in rule or not rule['optional']:
                self.matched = False
                return string

        self.matched = True
        return string

    def process_regexp( self, string, rule, next_rule ):

        # we need the regular expression, of course
        if not 'value' in rule:
            raise ValueError( 'Missing regular expression for rule %s in %s.  Include as "value" key' % ( rule, self.__class__ ) )

        # apply the regular expression!
        result = re.match( rule['value'], string, re.IGNORECASE )

        # if it didn't match then nothing channged
        if not result:
            return ( string, False )

        # otherwise we have a match and can return as such
        value = result.group(0)
        cleaned = string[len(value):].strip()

        if result.groups():
            value = result.group(1)

        return ( cleaned, value )

    def process_literal( self, string, rule, next_rule ):

        # we need the value to match, of course
        if not 'value' in rule:
            raise ValueError( 'Missing literal value for rule %s in %s.  Include as "value" key' % ( rule, self.__class__ ) )

        # easy to check for a literal match at the beginning of string
        val_len = len( rule['value'] )
        if string[:val_len].lower() != rule['value'].lower():
            return ( string, False )

        # if we matched then clean!
        return ( string[val_len:].strip(), rule['value'] )

    def process_delimited( self, string, rule, next_rule ):

        if not 'separator' in rule:
            raise ValueError( 'Missing separator for rule %s' % rule )

        # assumption: delimiteds are always followed up by a literal
        if not next_rule or next_rule['type'] != 'literal' or not next_rule['value']:
            raise ValueError( "Delimited rules must be followed by a literal" )

        end = next_rule['value'].lower()
        end_len = len( end )

        # it's ugly, but we will do this one character at a time
        quote = rule['quote'] if 'quote' in rule else ''
        sep = rule['separator']
        has_word = False
        vals = []
        current = ''
        in_quote = False
        for ( index, char ) in enumerate( string ):

            # if we hit a quote then we need to start/finish a word
            if quote and char == quote:

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
                if char == sep:

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
            return ( string, False )

        # almost done: one last step.  Remove everything that we parsed from string.
        # we know what index we stopped at, so it is easy.
        return ( string[index:], vals )

    def process_children( self, string, rule, next_rule ):

        if not 'classes' in rule and not 'rules' in rule:
            raise ValueError( 'Missing classes for children rule %s in %s' % ( rule, self.__class ) )

        matches = []

        # we need to keep looping through the children looking for matches
        # to the string until we no longer get any matches.  Then return.
        c = 0
        while string:

            c += 1
            if c > 1000:
                raise ValueError( 'Max depth reached' )

            shortest_leftover = False
            best_match = False
            best_leftover = ''
            current_string = string

            for child in rule['classes']:

                # let the child parse the string
                child_parser = child()
                leftover = child_parser.parse( current_string )

                # if it didn't do anything then this child didn't match
                if not child_parser.matched:
                    continue

                # It is possible that more than one child matches.  If so,
                # prioritize the child that matches the largest part of the
                # string.  All else being equal, first come first serve
                if best_match:
                    if len( leftover ) < shortest_leftover:
                        shortest_leftover = len( leftover )
                        best_match = child_parser
                        best_leftover = leftover
                else:
                    shortest_leftover = len( leftover )
                    best_match = child_parser
                    best_leftover = leftover

            # we have a match!
            if best_match:
                string = best_leftover
                matches.append( best_match )

            # If we didn't find anything then we are completely done
            else:
                return ( string, matches )

        # the only way we would get here is if we matched the entire string
        return ( '', matches )
