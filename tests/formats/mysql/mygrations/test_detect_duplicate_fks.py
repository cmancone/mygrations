import unittest

from mygrations.formats.mysql.file_reader.database import database as database_reader
from mygrations.formats.mysql.file_reader.create_parser import create_parser
from mygrations.formats.mysql.mygrations.mygration import mygration

class test_detect_duplicate_fks( unittest.TestCase ):
    """ Duplicate foreign key names are not allowed, so we should complain about it """

    def test_no_duplicate_fks_in_same_table( self ):
        table = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`account_id` INT(10) UNSIGNED NOT NULL,
`repeating_task_id` INT(10) UNSIGNED NOT NULL,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `account_id_tasks` (`account_id`),
KEY `repeating_task_id_tasks` (`repeating_task_id`),
CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`repeating_task_id`) REFERENCES `repeating_tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        tables = [ table ]
        db = database_reader( tables )

        self.assertEquals(["Found more than one constraint named 'account_id_tasks_fk' for table 'tasks'"], db.errors)

    def test_no_duplicate_fks_in_database( self ):
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
        tables = [ table1, table2 ]
        db = database_reader( tables )

        # I'm here: I need to enforce no duplciate foreign key names across the whole database
        self.assertFalse(True)
