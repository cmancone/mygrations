import unittest

from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.drivers.mysqldb.mysqldb import mysqldb
from tests.mocks.db.mysql.db_structure import db_structure
from mygrations.formats.mysql.mygrations.row_mygration import row_mygration

class test_mygrate_rows_simple( unittest.TestCase ):

    def _get_tables( self ):

        return {
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

    def test_add_rows( self ):

        # I could also just create the database and add rows but I feel like doing this
        tables = self._get_tables()
        rows = {
            'logs': (
                { 'id': 1, 'message': 'hey', 'traceback': 'never' },
                { 'id': 2, 'message': 'sup', 'traceback': 'forever' }
            )
        }

        database = database_reader( mysqldb( db_structure( tables, rows ) ) )
        database.read_rows( 'logs' )

        operations = [ str( op ) for op in row_mygration( database ).operations ]
        self.assertTrue( "INSERT INTO `logs` (`id`, `message`, `traceback`) VALUES ('1', 'hey', 'never');", operations[0] )
        self.assertTrue( "INSERT INTO `logs` (`id`, `message`, `traceback`) VALUES ('2', 'sup', 'forever');", operations[1] )
