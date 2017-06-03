import re

class parser( object ):

    num_rules = 0;
    rules = [ { 'type': 'regexp', 'value': '\S+', 'name': 'field' }, { 'type': 'literal', 'value': 'enum' }, { 'type': 'literal', 'value': '(' }, { 'type': 'delimited', 'name': 'values', 'quote': "'", 'separator': ',' }, { 'type': 'literal', 'value': ')' }, { 'type': 'regexp', 'value': 'default \S+', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True } ]

    _values = {}
    matched = False

    def __init__( self, rules = [] ):

        # rules should be defined by the subclass
        if rules:
            self.rules = rules

        if not self.rules:
            raise ValueError( "Cannot extend parser without providing rules" )

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

    def parse( self, string = 'created date, order_by int(10) unsigned not null default 0' ):

        # first thing first, some initial string cleaning.  Clean spaces
        # from start and end and replace any multi-spaces with a single space.
        string = re.sub( '\s+', ' ', string ).strip()

        for ( rule_index, rule ) in enumerate( self.rules ):

            # we always need a type
            if not 'type' in rule:
                raise ValueError( 'Missing type for rule %s' % rule )

            # we need a name for every rule but literal
            if not 'name' in rule and rule['type'] != 'literal':
                raise ValueError( 'Missing name for rule %s' % rule )

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

                raise ValueError( 'Unknown rule type: %s for rule %s' % ( rule['type'], rule ) )

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

        # if we got here then we got to the end: we parsed!
        self.matched = True
        return string

    def process_regexp( self, string, rule, next_rule ):

        # we need the regular expression, of course
        if not 'value' in rule:
            raise ValueError( 'Missing regular expression for rule %s.  Include as "value" key' % ( rule ) )

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
            raise ValueError( 'Missing literal value for rule %s.  Include as "value" key' % ( rule ) )

        # easy to check for a literal match at the beginning of string
        val_len = len( rule['value'] )
        if string[:val_len] != rule['value'].lower():
            return ( string, False )

        # if we matched then clean!
        return ( string[val_len:].strip(), rule['value'] )

    def process_delimited( self, string, rule, next_rule ):

        if not 'separator' in rule:
            raise ValueError( 'Missing separator for rule %s' % rule )

        # assumption: delimiteds are always followed up by a literal
        if not next_rule or next_rule['type'] != 'literal' or not next_rule['value']:
            raise ValueError( "Delimited rules must be followed by a literal" )

        end = next_rule['value']
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
                if string[index+1:index+1+end_len] == end:
                    if has_word:
                        current += char
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
        return ( string[index+1:], vals )

    def process_children( self, string, rule, next_rule ):

        return ( string, False )
