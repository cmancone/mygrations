import unittest

from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.drivers.mysqldb.mysqldb import mysqldb
from tests.mocks.db.mysql.db_structure import db_structure
class test_database(unittest.TestCase):
    def _get_tables(self):

        return {
            'logs':
            """
                CREATE TABLE `logs` (
                    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                    `message` TEXT NOT NULL,
                    `traceback` text,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""",
            'more_logs':
            """
                CREATE TABLE `more_logs` (
                    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                    `more_messages` TEXT NOT NULL,
                    `traceback` text,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }

    def test_simple(self):

        tables = self._get_tables()

        mock_db = db_structure(tables, {})
        database = database_reader(mysqldb(mock_db))

        # our parser should have a table!
        self.assertTrue('logs' in database.tables)
        self.assertTrue('more_logs' in database.tables)

    def test_read_rows(self):

        tables = self._get_tables()
        rows = {
            'logs': ({
                'id': 1,
                'message': 'hey',
                'traceback': 'never'
            }, {
                'id': 2,
                'message': 'sup',
                'traceback': 'forever'
            })
        }

        database = database_reader(mysqldb(db_structure(tables, rows)))

        # quick double check
        self.assertTrue('logs' in database.tables)
        self.assertTrue('more_logs' in database.tables)

        database.read_rows('logs')

        self.assertTrue(database.tables['logs'].tracking_rows)
        rows = database.tables['logs'].rows
        self.assertEquals(1, rows[1]['id'])
        self.assertEquals('hey', rows[1]['message'])
        self.assertEquals('never', rows[1]['traceback'])

        self.assertEquals(2, rows[2]['id'])
        self.assertEquals('sup', rows[2]['message'])
        self.assertEquals('forever', rows[2]['traceback'])
