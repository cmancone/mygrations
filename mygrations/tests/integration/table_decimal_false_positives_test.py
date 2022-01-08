import unittest

from mygrations.formats.mysql.file_reader.create_parser import CreateParser
class TableDecimalFalsePositivesTest(unittest.TestCase):
    def test_decimal_false_positives(self):
        """ false positives for change on default for decimal columns

        The default value for float and decimal columns can have the same issue for
        equality checking as any other floating comparison.  If the user's file sets
        the default to `0` mysql will return a default of '0.00', leading to a false
        detection of a column change and unnecessary database changes.
        """
        from_table = CreateParser()
        from_table.parse(
            """CREATE TABLE `decimal_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` decimal(20,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
) ENGINE=InnoDB;
        """
        )

        to_table = CreateParser()
        to_table.parse(
            """CREATE TABLE `decimal_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` decimal(20,2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
) ENGINE=InnoDB;
        """
        )

        self.assertEquals(0, len(from_table.to(to_table)))

    def test_decimal_false_positives_just_because(self):
        """ This probably isn't a realistic test, but let's go for it while we're here """
        from_table = CreateParser()
        from_table.parse(
            """CREATE TABLE `decimal_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` decimal(20,2) NOT NULL DEFAULT '1.007',
  PRIMARY KEY (`id`),
) ENGINE=InnoDB;
        """
        )

        to_table = CreateParser()
        to_table.parse(
            """CREATE TABLE `decimal_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` decimal(20,2) NOT NULL DEFAULT '1.008',
  PRIMARY KEY (`id`),
) ENGINE=InnoDB;
        """
        )

        self.assertEquals(0, len(from_table.to(to_table)))

    def test_decimal_real_positives(self):
        from_table = CreateParser()
        from_table.parse(
            """CREATE TABLE `decimal_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` decimal(20,2) NOT NULL DEFAULT '1.00',
  PRIMARY KEY (`id`),
) ENGINE=InnoDB;
        """
        )

        to_table = CreateParser()
        to_table.parse(
            """CREATE TABLE `decimal_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` decimal(20,2) NOT NULL DEFAULT '1.01',
  PRIMARY KEY (`id`),
) ENGINE=InnoDB;
        """
        )

        self.assertEquals(1, len(from_table.to(to_table)))

    def test_float_false_positives(self):
        from_table = CreateParser()
        from_table.parse(
            """CREATE TABLE `decimal_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` float NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
) ENGINE=InnoDB;
        """
        )

        to_table = CreateParser()
        to_table.parse(
            """CREATE TABLE `decimal_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` float NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
) ENGINE=InnoDB;
        """
        )

        self.assertEquals(0, len(from_table.to(to_table)))
