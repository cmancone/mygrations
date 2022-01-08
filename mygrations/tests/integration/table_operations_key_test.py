import unittest

from mygrations.formats.mysql.file_reader.create_parser import CreateParser
from mygrations.formats.mysql.definitions.index import Index
class TableOperationsKeyTest(unittest.TestCase):
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

    def test_add_index(self):
        table = self._get_default_table()
        self.assertTrue(table.column_is_indexed('account_id'))

        table.add_index(Index('task_tasks', ['task', 'subject']))
        self.assertTrue('task_tasks' in table.indexes)
        self.assertTrue(table.column_is_indexed('task'))

    def test_cannot_add_duplicate_key(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.add_index(Index('tasks_account_id', ['task', 'subject']))

    def test_remove_index(self):
        table = self._get_default_table()
        self.assertTrue(table.column_is_indexed('account_id'))

        table.remove_index('tasks_account_id')
        self.assertFalse('tasks_account_id' in table.indexes)
        self.assertFalse(table.column_is_indexed('account_id'))

    def test_cannot_remove_missing_key(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.remove_index('asdf')

    def test_change_index(self):
        table = self._get_default_table()
        self.assertTrue(table.column_is_indexed('account_id'))

        table.change_index(Index('tasks_account_id', ['account_id', 'task']))
        self.assertEquals('KEY `tasks_account_id` (`account_id`,`task`)', str(table.indexes['tasks_account_id']))
        self.assertTrue(table.column_is_indexed('account_id'))

    def test_cannot_change_missing_key(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.change_index(Index('asdf', ['account_id', 'task']))
