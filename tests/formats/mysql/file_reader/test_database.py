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
        database = database_reader( strings )

        # our parser should have a table!
        self.assertTrue( 'logs' in database.tables )
        self.assertTrue( 'more_logs' in database.tables )

    def test_with_rows( self ):

        strings = ["""
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        ""","""
            INSERT INTO logs (id,message,traceback) VALUES (1,'hi','sup'),(2,'what','kay');
        """]
        database = database_reader( strings )

        # our parser should have a table!
        self.assertTrue( 'logs' in database.tables )
        self.assertEquals( 3, database.tables['logs'].auto_increment )

        rows = database.tables['logs'].rows
        self.assertEquals( 'hi', rows[1]['message'] )
        self.assertEquals( 'sup', rows[1]['traceback'] )
        self.assertEquals( 'what', rows[2]['message'] )
        self.assertEquals( 'kay', rows[2]['traceback'] )

    def test_keeps_errors( self ):

        strings = ["""
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT DEFAULT '',
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """]
        database = database_reader( strings )

        self.assertTrue( 'not allowed to have a default value for column message in table logs' in database.errors[0] )
