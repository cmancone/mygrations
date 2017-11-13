import unittest

from mygrations.formats.mysql.db_reader.database import database as database_reader
from mygrations.formats.mysql.file_reader.database import database as file_reader
from mygrations.drivers.mysqldb.mysqldb import mysqldb
from tests.mocks.db.mysql.db_structure import db_structure
from mygrations.formats.mysql.mygrations.row_mygration import row_mygration


class test_quotes( unittest.TestCase ):

    def test_diffs_with_quotes( self ):
        """ Things that need quotes can cause trouble """

        # stick close to our use case: get the comparison table from the "database"
        tables = {
            'logs': """
                CREATE TABLE `logs` (
                    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                    `message` TEXT NOT NULL,
                    `traceback` text,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }

        rows = {
            'logs': (
                { 'id': 1, 'message': 'test\\sup', 'traceback': 'never' },
                { 'id': 2, 'message': 'sup\\test', 'traceback': 'forever' }
            )
        }

        db_db = database_reader( mysqldb( db_structure( tables, rows ) ) )
        db_db.read_rows( 'logs' )

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
        files_db = file_reader( [ table1 ] )

        mygrate = row_mygration( files_db, db_db )
        for op in mygrate:
            print( str( op ) )
