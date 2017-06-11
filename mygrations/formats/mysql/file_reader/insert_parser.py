from mygrations.core.parse.parser import parser

from .parsers import *

class insert_parser( parser ):

    string = ''

    rules = [
        { 'type': 'literal', 'value': 'INSERT INTO' },
        { 'type': 'regexp', 'value': '[^\s\(]+', 'name': 'table' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'delimited', 'name': 'fields', 'separator': ',', 'quote': '`' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': 'VALUES' },
        { 'type': 'children', 'name': 'inserts', 'classes': [ insert_values ] },
        { 'type': 'literal', 'value': ';', 'optional': True, 'name': 'closing_semicolon' }
    ]
