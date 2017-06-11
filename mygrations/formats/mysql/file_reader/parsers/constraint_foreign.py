from mygrations.core.parse.parser import parser

class constraint_foreign( parser ):

    # CONSTRAINT `accounts_status_id_ref_account_statuses_id` FOREIGN KEY (`status_id`) REFERENCES `account_statuses` (`id`) ON UPDATE CASCADE
    rules = [
        { 'type': 'literal', 'value': 'CONSTRAINT' },
        { 'type': 'regexp', 'name': 'constraint_name', 'value': '[^\(\s\)]+' },
        { 'type': 'literal', 'value': 'FOREIGN KEY (' },
        { 'type': 'regexp', 'name': 'field_name', 'value': '[^\(\s\)]+' },
        { 'type': 'literal', 'value': ') REFERENCES' },
        { 'type': 'regexp', 'name': 'foreign_table', 'value': '[^\(]+' },
        { 'type': 'literal', 'value': '(' },
        { 'type': 'regexp', 'name': 'foreign_field', 'value': '[^\)]+' },
        { 'type': 'literal', 'value': ')' },
        { 'type': 'literal', 'value': 'ON DELETE CASCADE', 'optional': True },
        { 'type': 'literal', 'value': 'ON DELETE NO ACTION', 'optional': True },
        { 'type': 'literal', 'value': 'ON DELETE RESTRICT', 'optional': True },
        { 'type': 'literal', 'value': 'ON DELETE SET DEFAULT', 'optional': True },
        { 'type': 'literal', 'value': 'ON DELETE SET NULL', 'optional': True },
        { 'type': 'literal', 'value': 'ON UPDATE CASCADE', 'optional': True },
        { 'type': 'literal', 'value': 'ON UPDATE NO ACTION', 'optional': True },
        { 'type': 'literal', 'value': 'ON UPDATE RESTRICT', 'optional': True },
        { 'type': 'literal', 'value': 'ON UPDATE SET DEFAULT', 'optional': True },
        { 'type': 'literal', 'value': 'ON UPDATE SET NULL', 'optional': True },
        { 'type': 'literal', 'value': ',', 'optional': True, 'name': 'ending_comma' }
    ]
