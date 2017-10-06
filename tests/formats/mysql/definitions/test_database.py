import unittest

from mygrations.formats.mysql.file_reader.database import database as database_reader
from mygrations.formats.mysql.file_reader.create_parser import create_parser

class test_database( unittest.TestCase ):

    def _get_sample_db( self ):

        strings = ["""
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        ""","""
            CREATE TABLE `more_logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `more_messages` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """]
        return database_reader( strings )

    def test_simple( self ):

        db1 = self._get_sample_db()
        strings = ["""
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        ""","""
            CREATE TABLE `less_logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `more_messages` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """]
        db2 = database_reader( strings )

        #differences = db2 - db1
        #self.assertEquals( [], differences )

    def test_add_table( self ):
        db = self._get_sample_db()

        new_table = create_parser()
        new_table.parse( """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `type_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            KEY `log_changes_type_id` (`type_id`)
            );
        """ )

        db.add_table( new_table )

        self.assertEquals( 3, len( db.tables ) )
        self.assertTrue( 'log_changes' in db.tables )
        self.assertEquals( new_table, db.tables['log_changes'] )
