import unittest

from mygrations.formats.mysql.file_reader.database import database as database_reader
from mygrations.formats.mysql.file_reader.create_parser import create_parser
from mygrations.formats.mysql.mygrations.mygration import mygration

class test_detect_duplicate_indexes( unittest.TestCase ):
    """ Duplicate index names are not allowed, so we should complain about it """

    def test_no_duplicate_indexes_in_same_table( self ):
        table = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`account_id` INT(10) UNSIGNED NOT NULL,
`repeating_task_id` INT(10) UNSIGNED NOT NULL,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `account_id_tasks` (`account_id`),
KEY `account_id_tasks` (`account_id`,`name`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        tables = [ table ]
        db = database_reader( tables )

        self.assertEquals(["Found more than one index named 'account_id_tasks' for table 'tasks'"], db.errors)
