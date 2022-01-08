import unittest

from mygrations.formats.mysql.file_reader.create_parser import CreateParser
from mygrations.core.definitions.columns.column import Column
class TableOperationsColumnTest(unittest.TestCase):
    def _get_default_table(self):
        table = CreateParser()
        table.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            `subject` varchar(255) NOT NULL DEFAULT '',
            PRIMARY KEY (id),
            KEY `tasks_account_id` (`account_id`),
            CONSTRAINT `tasks_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """
        )

        return table

    def _get_new_column(self):
        return Column(**{"name": "description", "column_type": "TEXT", "length": ""})

    def test_add_column_before(self):
        table = self._get_default_table()
        table.add_column(self._get_new_column(), 'task')

        self.assertTrue('description' in table.columns)
        self.assertEquals('task', table.column_before('description'))

    def test_add_column_first(self):
        table = self._get_default_table()
        table.add_column(self._get_new_column(), True)

        self.assertTrue('description' in table.columns)
        self.assertTrue(table.column_before('description'))

    def test_add_column_last(self):
        table = self._get_default_table()
        table.add_column(self._get_new_column(), False)

        self.assertTrue('description' in table.columns)
        self.assertEquals('subject', table.column_before('description'))

    def test_add_column_after_non_existent(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.add_column(self._get_new_column(), 'asdfef')

    def test_cannot_add_duplicate_column(self):
        table = self._get_default_table()
        table.add_column(self._get_new_column())
        with self.assertRaises(ValueError):
            table.add_column(self._get_new_column())

    def test_remove_column(self):
        table = self._get_default_table()
        table.remove_column('task')
        self.assertFalse('task' in table.columns)

    def test_change_column(self):
        table = self._get_default_table()
        new_subject = Column(**{"name": "subject", "column_type": "TEXT", "length": ""})
        table.change_column(new_subject)

        self.assertEquals('`subject` TEXT', str(table.columns['subject']))

    def test_change_column_no_rename(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.change_column(self._get_new_column())
