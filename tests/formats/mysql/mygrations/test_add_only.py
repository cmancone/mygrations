import unittest

from mygrations.formats.mysql.file_reader.database import database as database_reader
from mygrations.formats.mysql.file_reader.create_parser import create_parser
from mygrations.formats.mysql.mygrations.mygration import mygration

class test_add_only( unittest.TestCase ):

    def test_add_one_only( self ):
        """ mygration can accept only one table, in which case it just figures out the proper add order

        If there are no foreign key constraints, then it will "add" them in random order
        """

        table1 = "CREATE TABLE `zlogs` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,\n`message` TEXT NOT NULL,\n`traceback` TEXT,\nPRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        table2 = "CREATE TABLE `people` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,\n`first_name` VARCHAR(255) NOT NULL DEFAULT '',\n`last_name` VARCHAR(255) NOT NULL DEFAULT '',\nPRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        tables = [ table1, table2 ]
        db = database_reader( tables )
        mygrate = mygration( db )
        ops = [ str( op ) for op in mygrate.operations ]

        self.assertTrue( table1 in ops )
        self.assertTrue( table2 in ops )
