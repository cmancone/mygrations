import unittest

from mygrations.formats.mysql.file_reader.create_parser import CreateParser
class TableTextFalsePositives(unittest.TestCase):
    def test_row_false_positives(self):
        """ Complicated false positives for changes on text columns

        Even if you don't specify a COLLATE or CHARACTER SET on a text column, MySQL
        may still return a COLLATE or CHARACTER SET in the `SHOW CREATE TABLE` command

        You can verify that by running these two queries:

            >>> CREATE TABLE `collate_false_positive` (
            >>>   `quickbooks_log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            >>>   `quickbooks_ticket_id` int(10) unsigned DEFAULT NULL,
            >>>   `batch` int(10) unsigned NOT NULL,
            >>>   `msg` text NOT NULL,
            >>>   `log_datetime` datetime NOT NULL,
            >>>   PRIMARY KEY (`quickbooks_log_id`),
            >>>   KEY `quickbooks_ticket_id` (`quickbooks_ticket_id`),
            >>>   KEY `batch` (`batch`)
            >>> ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
            >>>
            >>> SHOW CREATE TABLE collate_false_positive;

        The output of the CREATE TABLE will include: `msg text COLLATE utf8_unicode_ci NOT NULL`
        which is not found in the original create table command.  If we assume (which we do)
        that any difference between the input and the output (from `SHOW CREATE TABLE`) means
        that the table needs to be altered, then this will result in us attempting to
        alter this table every time we migrate, with no affect.  This test makes sure
        we don't all into this false-positive trap.
        """
        from_table = CreateParser()
        from_table.parse(
            """CREATE TABLE `collate_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `msg` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
        """
        )

        to_table = CreateParser()
        to_table.parse(
            """CREATE TABLE `collate_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `msg` text NOT NULL,
  PRIMARY KEY (`id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
        """
        )

        self.assertEquals(0, len(from_table.to(to_table)))

    def test_false_positive_didnt_break_real_positives(self):
        """ Make sure that the above false-positive correction didn't break real-positive detections """

        from_table = CreateParser()
        from_table.parse(
            """CREATE TABLE `collate_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `msg` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
        """
        )

        to_table = CreateParser()
        to_table.parse(
            """CREATE TABLE `collate_false_positive` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `msg` text COLLATE latin2_general_ci NOT NULL,
  PRIMARY KEY (`id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
        """
        )

        ops = [str(val) for val in from_table.to(to_table)]
        self.assertEquals(
            "ALTER TABLE `collate_false_positive` CHANGE `msg` `msg` TEXT NOT NULL COLLATE 'LATIN2_GENERAL_CI';", ops[0]
        )

    def test_table_false_positives(self):
        """ This same basic bug happens at the table-level in a different way

        Even if you don't specify a COLLATE or CHARACTER SET on the table, MySQL
        may still return a COLLATE or CHARACTER SET in the `SHOW CREATE TABLE` command,
        with the value set by the default for the database.

        You can verify that by running these two queries:

            >>> CREATE TABLE `collate_false_positive` (
            >>>   `quickbooks_log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            >>>   `quickbooks_ticket_id` int(10) unsigned DEFAULT NULL,
            >>>   `batch` int(10) unsigned NOT NULL,
            >>>   `msg` text NOT NULL,
            >>>   `log_datetime` datetime NOT NULL,
            >>>   PRIMARY KEY (`quickbooks_log_id`),
            >>>   KEY `quickbooks_ticket_id` (`quickbooks_ticket_id`),
            >>>   KEY `batch` (`batch`)
            >>> ) ENGINE=InnoDB;
            >>>
            >>> SHOW CREATE TABLE collate_false_positive;

        The output of the CREATE TABLE will include: `ENGINE=InnoDB DEFAULT CHARSET=latin1;`
        which is not found in the original create table command.  If we assume (which we do)
        that any difference between the input and the output (from `SHOW CREATE TABLE`) means
        that the table needs to be altered, then this will result in us attempting to
        alter this table every time we migrate, with no affect.  This test makes sure
        we don't all into this false-positive trap.
        """
        pass
