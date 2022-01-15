import unittest

from mygrations.formats.mysql.db_reader.database import Database as DatabaseReader
from mygrations.drivers.pymysql.pymysql import PyMySQL
from mygrations.tests.mocks.db.mysql.db_structure import DbStructure
from mygrations.formats.mysql.mygrations.row_mygration import RowMygration
class MygrateRowsSimpleTest(unittest.TestCase):
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

    def test_add_rows(self):

        # I could also just create the database and add rows but I feel like doing this
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

        database = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows)))
        database.read_rows('logs')

        operations = [str(op) for op in RowMygration(database).operations]
        self.assertEquals(2, len(operations))
        self.assertEquals(
            "INSERT INTO `logs` (`id`, `message`, `traceback`) VALUES ('1', 'hey', 'never');", operations[0]
        )
        self.assertEquals(
            "INSERT INTO `logs` (`id`, `message`, `traceback`) VALUES ('2', 'sup', 'forever');", operations[1]
        )

    def test_modify_rows(self):

        # I could also just create the database and add rows but I feel like doing this
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

        database = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows)))
        database.read_rows('logs')

        rows_from = {
            'logs': ({
                'id': 1,
                'message': 'hey',
                'traceback': 'bah'
            }, {
                'id': 2,
                'message': 'sup',
                'traceback': 'forever'
            })
        }
        database_from = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows_from)))
        database_from.read_rows('logs')

        operations = [str(op) for op in RowMygration(database, database_from).operations]
        self.assertEquals(1, len(operations))
        self.assertEquals("UPDATE `logs` SET `message`='hey', `traceback`='never' WHERE id='1';", operations[0])

    def test_delete_rows(self):

        # I could also just create the database and add rows but I feel like doing this
        tables = self._get_tables()
        rows = {'logs': ({'id': 2, 'message': 'sup', 'traceback': 'forever'}, )}

        database = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows)))
        database.read_rows('logs')

        rows_from = {
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
        database_from = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows_from)))
        database_from.read_rows('logs')

        operations = [str(op) for op in RowMygration(database, database_from).operations]
        self.assertEquals(1, len(operations))
        self.assertEquals("DELETE FROM `logs` WHERE id='1';", operations[0])

    def test_all(self):

        # I could also just create the database and add rows but I feel like doing this
        tables = self._get_tables()
        rows = {
            'logs': ({
                'id': 2,
                'message': 'sup',
                'traceback': 'whatever'
            }, {
                'id': 3,
                'message': 'okay',
                'traceback': 'always'
            })
        }

        database = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows)))
        database.read_rows('logs')

        rows_from = {
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
        database_from = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows_from)))
        database_from.read_rows('logs')

        operations = [str(op) for op in RowMygration(database, database_from).operations]
        # don't be picky about the order
        self.assertEquals(3, len(operations))
        self.assertTrue(
            "INSERT INTO `logs` (`id`, `message`, `traceback`) VALUES ('3', 'okay', 'always');" in operations
        )
        self.assertTrue("DELETE FROM `logs` WHERE id='1';" in operations)
        self.assertTrue("UPDATE `logs` SET `message`='sup', `traceback`='whatever' WHERE id='2';" in operations)
