import unittest

from mygrations.formats.mysql.file_reader.create_parser import create_parser
from mygrations.formats.mysql.definitions.index import index
class test_table_operations_key(unittest.TestCase):
    def _get_default_table(self):
        table = create_parser()
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

    def test_add_key(self):
        table = self._get_default_table()
        self.assertTrue(table.column_is_indexed('account_id'))

        table.add_key(index('task_tasks', ['task', 'subject']))
        self.assertTrue('task_tasks' in table.indexes)
        self.assertTrue(table.column_is_indexed('task'))

    def test_cannot_add_duplicate_key(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.add_key(index('tasks_account_id', ['task', 'subject']))

    def test_remove_key(self):
        table = self._get_default_table()
        self.assertTrue(table.column_is_indexed('account_id'))

        table.remove_key('tasks_account_id')
        self.assertFalse('tasks_account_id' in table.indexes)
        self.assertFalse(table.column_is_indexed('account_id'))

    def test_cannot_remove_missing_key(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.remove_key('asdf')

    def test_change_key(self):
        table = self._get_default_table()
        self.assertTrue(table.column_is_indexed('account_id'))

        table.change_key(index('tasks_account_id', ['account_id', 'task']))
        self.assertEquals('KEY `tasks_account_id` (`account_id`,`task`)', str(table.indexes['tasks_account_id']))
        self.assertTrue(table.column_is_indexed('account_id'))

    def test_cannot_change_missing_key(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.change_key(index('asdf', ['account_id', 'task']))
