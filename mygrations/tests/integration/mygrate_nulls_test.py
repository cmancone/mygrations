import unittest
from mygrations.formats.mysql.db_reader.database import Database as DatabaseReader
from mygrations.formats.mysql.file_reader.database import Database as FileReader
from mygrations.drivers.pymysql.pymysql import PyMySQL
from mygrations.tests.mocks.db.mysql.db_structure import DbStructure
from mygrations.formats.mysql.mygrations.row_mygration import RowMygration
class MygrateNullsTest(unittest.TestCase):
    def test_diff_with_null(self):
        """ NULL should be allowed and should result in a MySQL NULL in the database

        The system was turning NULL into a literal 'NULL'.  Internally, NULL
        is handled as a None
        """
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
            'logs': (
                {
                    'id': 1,
                    'message': 'from null to value',
                    'traceback': None
                },
                {
                    'id': 2,
                    'message': 'from value to null',
                    'traceback': 'forever'
                },
                {
                    'id': 3,
                    'message': 'from null to null',
                    'traceback': None
                },
            )
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

        INSERT INTO logs (id,message,traceback) VALUES (1,'from null to value', 'HEY');
        INSERT INTO logs (id,message,traceback) VALUES (2,'from value to null', NULL);
        INSERT INTO logs (id,message,traceback) VALUES (3,'from null to null', NULL);
        INSERT INTO logs (id,message,traceback) VALUES (4,'Insert Null',NULL);
        """
        files_db = FileReader([table1])

        mygrate = RowMygration(files_db, db_db)
        ops = [str(op) for op in mygrate]
        self.assertEquals(3, len(ops))
        self.assertTrue("INSERT INTO `logs` (`id`, `message`, `traceback`) VALUES ('4', 'Insert Null', NULL);" in ops)
        self.assertTrue("UPDATE `logs` SET `message`='from null to value', `traceback`='HEY' WHERE id='1';" in ops)
        self.assertTrue("UPDATE `logs` SET `message`='from value to null', `traceback`=NULL WHERE id='2';" in ops)
