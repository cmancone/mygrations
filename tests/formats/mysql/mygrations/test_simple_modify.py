import unittest

from mygrations.formats.mysql.file_reader.database import database as database_reader
from mygrations.formats.mysql.mygrations.mygration import mygration

class test_add_conflicting_fks( unittest.TestCase ):

    accounts_table = """CREATE TABLE `accounts` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    def _get_db1( self ):
        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) UNSIGNED NOT NULL,
            `repeating_task_id` INT(10) UNSIGNED NOT NULL,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`),
            KEY `repeating_task_id_tasks` (`repeating_task_id`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        return database_reader( [ table1, self.accounts_table ] )

    def test_simple_add_and_modify( self ):
        """ Migrate to a database that has one extra table and column """

        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) UNSIGNED NOT NULL,
            `repeating_task_id` INT(10) UNSIGNED NOT NULL,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            `subject` TEXT,
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`),
            KEY `repeating_task_id_tasks` (`repeating_task_id`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        table3 = """CREATE TABLE `histories` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        db2 = database_reader( [ table1, self.accounts_table, table3 ] )
        db1 = self._get_db1()

        mygrate = mygration( db2, db1 )

        self.assertEquals( table3, str( mygrate.operations[0] ) )
        self.assertEquals( 'ADD `subject` TEXT AFTER `name`', str( mygrate.operations[1] ) )

    def test_add_column_and_mutually_dependent_fk( self ):
        """ Add a column to a table that depends upon a table with a mutually-dependent FK """
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
CONSTRAINT `task_id_rts` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        db2 = database_reader( [ table1, table2, self.accounts_table ] )

        mygrate = mygration( db2, self._get_db1() )

        print( [ str( op ) for op in mygrate.operations ] )
