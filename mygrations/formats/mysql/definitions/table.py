from collections import OrderedDict
from .wrap_parser import wrap_parser

class table( object ):

    columns = None
    indexes = None
    constraints = None

    def __init__( self, parsed_table ):

        for parsed_definition in parsed_table.definitions:

            definition = wrap_parser( parsed_definition )
            print ( '%s %s' % ( parsed_definition.name, definition.__class__ ) )
            #print( '%s %s' % ( definition.name, definition.definition_type ) )

