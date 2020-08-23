import unittest
from .string import String


class TestString(unittest.TestCase):
    def test_string_conversion_with_collation(self):
        column = String(
            name='test_column',
            column_type='INT',
            length=25,
            default='asdf',
            character_set='unicode',
            collate='sup'
        )

        self.assertEquals('`test_column` INT(25) DEFAULT \'asdf\' CHARACTER SET \'UNICODE\' COLLATE \'SUP\'', str(column))

    def test_is_the_same(self):
        attrs = {
            'name': 'test',
            'column_type': 'VARCHAR',
            'length': 255,
            'character_set': 'unicode',
        }

        column1 = String(**attrs)
        column2 = String(**{**attrs, 'collate': 'hey'})

        # since collate is only present for one they are the same
        self.assertTrue(column1.is_really_the_same_as(column2))
        self.assertTrue(column2.is_really_the_same_as(column1))

        # but since they both have values but are different they are different
        column3 = String(**{**attrs, 'collate': 'sup'})
        self.assertFalse(column3.is_really_the_same_as(column2))
        self.assertFalse(column2.is_really_the_same_as(column3))
