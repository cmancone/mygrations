from mygrations.core.parse.parser import parser

class type_numeric( parser ):

    # `created` int(10) unsigned not null default 0 AUTO_INCREMENT
    rules = [ { 'type': 'regexp', 'value': '[^\(\s\)]+', 'name': 'field' }, { 'type': 'regexp', 'value': '\w+', 'name': 'type' }, { 'type': 'literal', 'value': '(' }, { 'type': 'regexp', 'value': '\d+', 'name': 'length' }, { 'type': 'literal', 'value': ')' }, { 'type': 'literal', 'value': 'unsigned', 'optional': True }, { 'type': 'literal', 'value': 'not null', 'optional': True }, { 'type': 'regexp', 'value': 'default [^\(\s\)]+', 'name': 'default', 'optional': True }, { 'type': 'literal', 'value': 'auto_increment', 'optional': True }, { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' } ]
