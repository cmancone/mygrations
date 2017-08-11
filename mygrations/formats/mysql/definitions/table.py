from collections import OrderedDict

class table( object ):

    columns = None
    indexes = None
    constraints = None
    primary_column = ''

    def __init__( self, parsed_table ):

        self.columns = OrderedDict()
        self.indexes = OrderedDict()
        self.constraints = OrderedDict()

        for parsed_definition in parsed_table.definitions:

            # we still have to do a little sorting
            if definition.definition_type == 'column':
                store_name = 'columns'
            elif definition.definition_type == 'index':
                store_name = 'indexes'
            elif definition.definition_type == 'primary':
                store_name = 'indexes'
                self.primary_column = definition.name
            elif definition.definition_type == 'constraint':
                store_name = 'constraints'

            store = getattr( self, store_name )
            store[definition.name] = definition
            setattr( self, store_name, store )

        #print( self.columns )
        #print( self.indexes )
        #print( self.constraints )
