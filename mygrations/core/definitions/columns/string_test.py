import unittest
from .string import String
class TestString(unittest.TestCase):
    def test_string_conversion_with_collation(self):
        column = String('test_column', 'VARCHAR', length=25, default='asdf', character_set='unicode', collate='sup')

        self.assertEquals(
            '`test_column` VARCHAR(25) DEFAULT \'asdf\' CHARACTER SET \'UNICODE\' COLLATE \'SUP\'', str(column)
        )
        self.assertEquals([], column.schema_errors)
        self.assertEquals([], column.schema_warnings)

    def test_is_the_same(self):
        attrs = {
            'length': 255,
            'character_set': 'unicode',
        }

        column1 = String('test', 'VARCHAR', **attrs)
        column2 = String('test', 'VARCHAR', **{**attrs, 'collate': 'hey'})

        # since collate is only present for one they are the same
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        # but since they both have values but are different they are different
        column3 = String('test', 'VARCHAR', **{**attrs, 'collate': 'sup'})
        self.assertFalse(column3.is_really_the_same_as(column2))
        self.assertFalse(column2.is_really_the_same_as(column3))

    def test_no_default(self):
        no_default = [
            'TINYBLOB',
            'BLOB',
            'MEDIUMBLOB',
            'LONGBLOB',
            'TINYTEXT',
            'TEXT',
            'MEDIUMTEXT',
            'LONGTEXT',
            'JSON',
        ]
        for column_type in no_default:
            column = String('test', column_type, default='Hey', has_default=True)
            self.assertEquals(
                [f"Column 'test' of type '{column_type}' cannot have a default"],
                column.schema_errors,
            )

    def test_no_character_set_or_collate(self):
        nope = [
            'TINYBLOB',
            'BLOB',
            'MEDIUMBLOB',
            'LONGBLOB',
            'TINYTEXT',
            'TEXT',
            'MEDIUMTEXT',
            'LONGTEXT',
            'JSON',
        ]
        for column_type in nope:
            column = String('test', column_type, character_set='Hey')
            self.assertEquals(
                [f"Column 'test' of type '{column_type}' cannot have a collation/character set"],
                column.schema_errors,
            )
            column = String('test', column_type, collate='Hey')
            self.assertEquals(
                [f"Column 'test' of type '{column_type}' cannot have a collation/character set"],
                column.schema_errors,
            )

    def test_no_length(self):
        no_length = [
            'TINYBLOB',
            'BLOB',
            'MEDIUMBLOB',
            'LONGBLOB',
            'TINYTEXT',
            'TEXT',
            'MEDIUMTEXT',
            'LONGTEXT',
            'JSON',
        ]
        for column_type in no_length:
            column = String('test', column_type, length='28')
            self.assertEquals(
                [f'Column test of type {column_type} cannot have a length'],
                column.schema_errors,
            )

    def test_binary_collation(self):
        binary_only = [
            'BINARY',
            'VARBINARY',
        ]
        for column_type in binary_only:
            column = String('test', column_type, character_set='Hey')
            self.assertEquals(
                [f"Column 'test' of type '{column_type}' can only have a collate/character set of BINARY"],
                column.schema_errors,
            )
            column = String('test', column_type, collate='Hey')
            self.assertEquals(
                [f"Column 'test' of type '{column_type}' can only have a collate/character set of BINARY"],
                column.schema_errors,
            )
            column = String('test', column_type, collate='binary')
            self.assertEquals([], column.schema_errors)
            column = String('test', column_type, character_set='binary')
            self.assertEquals([], column.schema_errors)
            column = String('test', column_type, character_set='binary', collate='binary')
            self.assertEquals([], column.schema_errors)

    def test_no_auto_increment(self):
        column = String('test', 'VARCHAR', auto_increment=True)
        self.assertEquals(
            [f"Column 'test' of type 'VARCHAR' cannot be an AUTO_INCREMENT: only numeric columns can"],
            column.schema_errors,
        )
