import unittest

from mygrations.formats.mysql.file_reader.database import Database as DatabaseReader
from mygrations.formats.mysql.file_reader.create_parser import CreateParser
from mygrations.formats.mysql.mygrations.mygration import Mygration
class AddConflictingForeignKeyTests(unittest.TestCase):
    def test_add_conflicting_separates_fks(self):
        """ 3 adds. """

        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`account_id` INT(10) UNSIGNED NOT NULL,
`repeating_task_id` INT(10) UNSIGNED NOT NULL,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `account_id_tasks` (`account_id`),
KEY `repeating_task_id_tasks` (`repeating_task_id`),
CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT `repeating_task_id_tasks_fk` FOREIGN KEY (`repeating_task_id`) REFERENCES `repeating_tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        table2 = """CREATE TABLE `repeating_tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`account_id` INT(10) UNSIGNED NOT NULL,
`task_id` INT(10) UNSIGNED NOT NULL,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `account_id_rts` (`account_id`),
KEY `task_id_rts` (`task_id`),
CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT `task_id_rts` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        table3 = """CREATE TABLE `accounts` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        tables = [table1, table2, table3]
        db = DatabaseReader(tables)
        mygrate = Mygration(db)

        self.assertEquals([
            "Duplicate foreign key: foreign key named 'account_id_tasks_fk' exists in tables 'tasks' and 'repeating_tasks'"
        ], mygrate.errors)
        self.assertEquals(None, mygrate.operations)
