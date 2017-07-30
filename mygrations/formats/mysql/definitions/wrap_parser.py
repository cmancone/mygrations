from .constraint import constraint
from .index import index
from .primary import primary
from .unique import unique
from .column import column

class_map = {
    'constraint':   constraint,
    'index':        index,
    'primary':      primary,
    'unique':       unique,
    'column':       column
}

def wrap_parser( parser ):

    if not parser.definition_type in class_map:
        raise ValueError( "Cannot process parser with a definition type of %s" % ( parser.definition_type ) )

    return class_map[parser.definition_type]( parser )
