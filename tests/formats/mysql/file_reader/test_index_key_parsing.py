import unittest

from mygrations.formats.mysql.file_reader.reader import reader
class test_index_key_parsing(unittest.TestCase):
    def test_simple(self):
        parser = reader()
        returned = parser.parse(
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` VARCHAR(255) NOT NULL DEFAULT '',
                KEY `logs_message` (`message`),
                INDEX `logs_traceback` (`traceback`),
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        )

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('logs' in parser.tables)

        self.assertTrue('logs_message' in parser.tables['logs'].indexes)
        self.assertTrue('logs_traceback' in parser.tables['logs'].indexes)
        self.assertEquals(['message'], parser.tables['logs'].indexes['logs_message'].columns)
        self.assertEquals(['traceback'], parser.tables['logs'].indexes['logs_traceback'].columns)

    def test_unique(self):
        parser = reader()
        returned = parser.parse(
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` VARCHAR(255) NOT NULL DEFAULT '',
                UNIQUE KEY `logs_message` (`message`),
                UNIQUE INDEX `logs_traceback` (`traceback`),
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        )

        # we should have matched
        self.assertTrue(parser.matched)
        self.assertEquals('', returned)
        self.assertTrue('logs' in parser.tables)

        self.assertTrue('logs_message' in parser.tables['logs'].indexes)
        self.assertTrue('logs_traceback' in parser.tables['logs'].indexes)
        self.assertEquals('UNIQUE', parser.tables['logs'].indexes['logs_message'].index_type)
        self.assertEquals('UNIQUE', parser.tables['logs'].indexes['logs_traceback'].index_type)
