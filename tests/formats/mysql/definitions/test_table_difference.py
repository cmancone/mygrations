import unittest

from mygrations.formats.mysql.file_reader.create_parser import create_parser

class test_table_difference( unittest.TestCase ):

    def test_add_columns( self ):

        # parse a typical foreign key constraint
        a = create_parser()
        a.parse( """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL
            );
        """ )

        b = create_parser()
        b.parse( """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `membership_id` int(10) unsigned not null,
            `task` varchar(255) DEFAULT NULL,
            `subject` text
            );
        """ )

        print( (a-b)[0] )
