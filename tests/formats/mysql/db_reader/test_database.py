import unittest

from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.drivers.mysqldb.mysqldb import mysqldb
from tests.mocks.db.mysql.db_structure import db_structure

class test_database( unittest.TestCase ):

    def test_simple( self ):

        tables = {
            'logs': """
                CREATE TABLE `logs` (
                    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                    `message` TEXT NOT NULL,
                    `traceback` text,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""",
            'more_logs': """
                CREATE TABLE `more_logs` (
                    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                    `more_messages` TEXT NOT NULL,
                    `traceback` text,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }

        mock_db = db_structure( tables, {} )
        database = database_reader( mysqldb( mock_db ) )

        # our parser should have a table!
        self.assertTrue( 'logs' in database.tables )
        self.assertTrue( 'more_logs' in database.tables )
