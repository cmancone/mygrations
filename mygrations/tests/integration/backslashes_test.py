import unittest

from mygrations.formats.mysql.db_reader.database import Database as DatabaseReader
from mygrations.formats.mysql.file_reader.database import Database as FileReader
from mygrations.drivers.pymysql.pymysql import PyMySQL
from mygrations.tests.mocks.db.mysql.db_structure import DbStructure
from mygrations.formats.mysql.mygrations.row_mygration import RowMygration
class test_backslashes(unittest.TestCase):
    def test_diffs_with_quotes(self):
        """ Things that need backslashes can cause trouble """

        # stick close to our use case: get the comparison table from the "database"
        tables = {
            'logs':
            """
                CREATE TABLE `logs` (
                    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                    `message` TEXT NOT NULL,
                    `traceback` text,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }

        rows = {
            'logs': ({
                'id': 1,
                'message': 'test\\sup',
                'traceback': 'never'
            }, {
                'id': 2,
                'message': 'sup\\test',
                'traceback': 'forever'
            })
        }

        db_db = DatabaseReader(PyMySQL(connection=DbStructure(tables, rows)))
        db_db.read_rows('logs')

        # and one from a file
        table1 = """CREATE TABLE `logs` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `message` TEXT NOT NULL,
            `traceback` text,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

        INSERT INTO logs (id,message,traceback) VALUES (1,'test\\sup', 'never');
        INSERT INTO logs (id,message,traceback) VALUES (2,'bob\\test', 'forever');
        """
        files_db = FileReader([table1])

        mygrate = RowMygration(files_db, db_db)
        ops = [str(op) for op in mygrate]
        self.assertEquals(1, len(ops))
        self.assertEquals("UPDATE `logs` SET `message`='bob\\\\test', `traceback`='forever' WHERE id='2';", ops[0])
