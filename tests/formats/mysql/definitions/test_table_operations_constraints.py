import unittest

from mygrations.formats.mysql.file_reader.create_parser import create_parser
from mygrations.formats.mysql.definitions.constraint import constraint
class test_table_operations_constraints(unittest.TestCase):
    def _get_default_table(self):
        table = create_parser()
        table.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `status_id` int(10) unsigned not null,
            `task` varchar(255) DEFAULT NULL,
            `subject` varchar(255) NOT NULL DEFAULT '',
            PRIMARY KEY (id),
            KEY `tasks_account_id` (`account_id`),
            KEY `tasks_status_id` (`status_id`),
            CONSTRAINT `tasks_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """
        )

        return table

    def _get_new_constraint(self):
        return constraint(
            **{
                "name": "status_id_fk",
                "column": "status_id",
                "foreign_table": "task_statuses",
                "foreign_column": "id",
                "on_delete": "RESTRICT",
                "on_update": "CASCADE"
            }
        )

    def test_add_constraint(self):
        table = self._get_default_table()
        table.add_constraint(self._get_new_constraint())
        self.assertTrue('status_id_fk' in table.constraints)

    def test_cannot_add_duplicate_constraint(self):
        table = self._get_default_table()
        table.add_constraint(self._get_new_constraint())
        with self.assertRaises(ValueError):
            table.add_constraint(self._get_new_constraint())

    def test_remove_constraint(self):
        table = self._get_default_table()
        table.remove_constraint('tasks_account_id_fk')
        self.assertFalse('tasks_account_id_fk' in table.constraints)

    def test_cannot_remove_missing_constraint(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.remove_constraint('asdf')

    def test_change_constraint(self):
        table = self._get_default_table()
        table.change_constraint(
            constraint(
                **{
                    "name": "tasks_account_id_fk",
                    "column": "account_id",
                    "foreign_table": "task_accounts",
                    "foreign_column": "id",
                    "on_delete": "RESTRICT",
                    "on_update": "SET NULL"
                }
            )
        )

        self.assertEquals(
            'CONSTRAINT `tasks_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `task_accounts` (`id`) ON DELETE RESTRICT ON UPDATE SET NULL',
            str(table.constraints['tasks_account_id_fk'])
        )

    def test_cannot_change_missing_constraint(self):
        table = self._get_default_table()
        with self.assertRaises(ValueError):
            table.change_constraint(self._get_new_constraint())
