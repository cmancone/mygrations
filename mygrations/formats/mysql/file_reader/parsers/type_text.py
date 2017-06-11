from mygrations.core.parse.parser import parser

class type_text( parser ):

    #***** Lint error if default is found for text field ******

    # description text charset utf8 collate utf8
    rules = [ { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': 'not null', 'optional': True }, { 'type': 'regexp', 'value': 'default [^\(\s\)]+', 'optional': True, 'name': 'default' }, { 'type': 'regexp', 'value': 'CHARACTER SET [^\(\s\)]+', 'name': 'characterset', 'optional': True }, { 'type': 'regexp', 'value': 'COLLATE [^\(\s\)]+', 'name': 'collate', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' } ]
