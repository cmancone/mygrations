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

        self.assertTrue( str( mygrate.operations[0] ) in tables )
        self.assertTrue( str( mygrate.operations[1] ) in tables )

    def test_add_only_resolves_fk_order( self ):
        """ If there are foreign keys the order of CREATEs will be set such that no foreign key errors will be generated
        """

        table1 = """CREATE TABLE `has_mult_fk` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`person_id` INT(10) UNSIGNED NOT NULL,
`has_fk_id` INT(10) UNSIGNED NOT NULL,
PRIMARY KEY (`id`),
KEY `person_id` (`person_id`),
KEY `has_fk_id` (`has_fk_id`),
CONSTRAINT `person_id_fk` FOREIGN KEY (`person_id`) REFERENCES `people` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT `has_fk_id_fk` FOREIGN KEY (`has_fk_id`) REFERENCES `has_fk` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        table2 = """CREATE TABLE `has_fk` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`person_id` INT(10) UNSIGNED NOT NULL,
PRIMARY KEY (`id`),
KEY `person_id` (`person_id`),
CONSTRAINT `person_id_fk` FOREIGN KEY (`person_id`) REFERENCES `people` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        table3 = """CREATE TABLE `people` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`first_name` VARCHAR(255) NOT NULL DEFAULT '',
`last_name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        tables = [ table1, table2, table3 ]
        db = database_reader( tables )
        mygrate = mygration( db )

        self.assertEquals( table3, str( mygrate.operations[0] ) )
        self.assertEquals( table2, str( mygrate.operations[1] ) )
        self.assertEquals( table1, str( mygrate.operations[2] ) )
