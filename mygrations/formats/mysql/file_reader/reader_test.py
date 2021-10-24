import unittest

from mygrations.formats.mysql.file_reader.reader import Reader
class ReaderTest(unittest.TestCase):
    def test_simple(self):

        parser = Reader()
        returned = parser.parse(
            """
            /* I should find and ignore comments */
            -- Of any variety
               # really
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            INSERT INTO logs (`id`,`message`,`traceback`) VALUES (1,'blah','gah');
            INSERT INTO test (id,status) VALUES (1,'New'),(2,'Old');
        """
        )

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have matched everything
        self.assertEquals('', returned)

        # our parser should have a table!
        self.assertTrue('logs' in parser.tables)
        # just check a few details
        self.assertEquals('logs', parser.tables['logs'].name)
        self.assertEquals(3, len(parser.tables['logs'].columns))

        # and some records!
        self.assertTrue('logs' in parser.rows)
        self.assertTrue('test' in parser.rows)
        self.assertEquals(['id', 'message', 'traceback'], parser.rows['logs'][0].columns)
