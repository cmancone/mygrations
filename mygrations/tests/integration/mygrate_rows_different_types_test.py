import unittest

from mygrations.formats.mysql.db_reader.database import Database as DatabaseReader
from mygrations.drivers.pymysql.pymysql import PyMySQL
from mygrations.tests.mocks.db.mysql.db_structure import DbStructure
from mygrations.formats.mysql.mygrations.row_mygration import RowMygration
class MygrateRowsDifferentTypesTest(unittest.TestCase):
    def _get_tables(self):

        return {
            'logs':
            """
                CREATE TABLE `logs` (
                    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                    `account_id` int(10) unsigned not null,
                    `message` TEXT NOT NULL,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }

    def test_modify_rows(self):
        """ Types can change depending on whether or not rows come out of files or the database.  As a result, equality comparison has to ignore type differences """

        # I could also just create the database and add rows but I feel like doing this
        tables = self._get_tables()
        rows = {'logs': ({'id': 1, 'account_id': 1, 'message': 'hey'}, {'id': 2, 'account_id': 1, 'message': 'sup'})}

        database = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows)))
        database.read_rows('logs')

        rows_from = {
            'logs': ({
                'id': 1,
                'account_id': '1',
                'message': 'hey'
            }, {
                'id': 2,
                'account_id': '1',
                'message': 'sup'
            })
        }
        database_from = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows_from)))
        database_from.read_rows('logs')

        operations = [str(op) for op in RowMygration(database, database_from).operations]
        self.assertEquals(0, len(operations))
