import unittest

from mygrations.formats.mysql.file_reader.reader import reader

class test_regressions( unittest.TestCase ):
    """ Some tests based off failing CREATE TABLE commands from our database when things were first being finished """

    def test_payment_request_types( self ):

        parser = reader()
        returned = parser.parse( """CREATE TABLE `payment_request_types` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `slug` VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `order_by` INT(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `order_by_payment_request_types` (`order_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO payment_request_types (id,name,slug,order_by) VALUES (1,'Standard','standard',1),(2,'Special Circumstances','emergency',2);""" )

        # we should have matched
        self.assertTrue( parser.matched )

        # and we should have matched everything
        self.assertEquals( '', returned )

        # we should not have any errors
        self.assertEquals( [], parser.errors )
