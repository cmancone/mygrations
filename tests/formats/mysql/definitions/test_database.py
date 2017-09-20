import unittest

from mygrations.formats.mysql.file_reader.database import database as database_reader

class test_database( unittest.TestCase ):

    def test_simple( self ):

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
        db1 = database_reader( strings )

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

        differences = db2 - db1
        #self.assertEquals( [], differences )
