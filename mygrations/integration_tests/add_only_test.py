import unittest

from mygrations.formats.mysql.file_reader.database import Database
from mygrations.formats.mysql.mygrations.mygration import Mygration
class AddOnlyTest(unittest.TestCase):
    def test_add_one_only(self):
        """ mygration can accept only one table, in which case it just figures out the proper add order

        If there are no foreign key constraints, then it will "add" them in random order
        """

        table1 = "CREATE TABLE `zlogs` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,\n`message` TEXT NOT NULL,\n`traceback` TEXT,\nPRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        table2 = "CREATE TABLE `people` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,\n`first_name` VARCHAR(255) NOT NULL DEFAULT '',\n`last_name` VARCHAR(255) NOT NULL DEFAULT '',\nPRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        tables = [table1, table2]
        mygrate = Mygration(Database(tables))
        self.assertEquals([], mygrate.errors)
        ops = [str(op) for op in mygrate.operations]

        self.assertTrue(table1 in ops)
        self.assertTrue(table2 in ops)
