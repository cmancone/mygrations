import unittest

from mygrations.formats.mysql.file_reader.database import database as database_reader
from mygrations.formats.mysql.file_reader.create_parser import create_parser
from mygrations.formats.mysql.mygrations.mygration import mygration
class test_add_conflicting_fks(unittest.TestCase):
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
        db = database_reader(tables)
        mygrate = mygration(db)

        ops = [str(op) for op in mygrate.operations]

        self.assertEquals('SET FOREIGN_KEY_CHECKS=0;', ops[0])
        self.assertTrue(table1 in ops)
        self.assertTrue(table2 in ops)
        self.assertTrue(table3 in ops)
        self.assertEquals('SET FOREIGN_KEY_CHECKS=1;', ops[4])
