class rule_base( object ):

    require_name = True
    require_value = True
    require_next = False

    parser_class = ''
    rule = {}
    next_rule = {}
    name = ''
    result = ''
    leftovers = ''

    def __init__( self, parser, rule, next_rule ):

        # we keep parser class around just for reference and better errors
        self.parser_class = parser.__class__

        # store rule and next_rule
        self.rule = rule
        self.next_rule = next_rule

        self.name = self.rule['name'] if 'name' in self.rule else ''

        # name is requied more often than not
        if self.require_name and not self.name:
            raise ValueError( "name required for rule %s in class %s" % ( self.rule, self.parser_class ) )

        # ditto rule
        if self.require_value and not 'value' in self.rule or not self.rule['value']:
            raise ValueError( 'missing value in rule %s for class %s' % ( self.rule, self.parser_class ) )

    def parse( self, string ):

        # why is this here?  Because python abstract classes are stange, and I don't feel like bothering with them.
        # this accomplishes the exact same thing, just at run-time instead of compile-time.  Not a big deal
        # in this case.
        raise ValueError( "You forgot to extend rule_base.parse" )
