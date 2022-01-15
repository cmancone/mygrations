import unittest

from mygrations.formats.mysql.file_reader.create_parser import CreateParser
class TableDifferenceColumnsTest(unittest.TestCase):
    def test_drop_columns(self):

        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL
            );
        """
        )

        b = CreateParser()
        b.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `membership_id` int(10) unsigned not null,
            `task` varchar(255) DEFAULT NULL,
            `subject` text
            );
        """
        )

        # if we subtract b from a we should get some drop column queries in one alter statement
        operations = b.to(a)
        self.assertEquals(1, len(operations))
        self.assertEquals('ALTER TABLE `tasks` DROP membership_id, DROP subject;', str(operations[0]))

    def test_add_columns(self):

        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL
            );
        """
        )

        b = CreateParser()
        b.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `membership_id` int(10) unsigned not null,
            `task` varchar(255) DEFAULT NULL,
            `subject` text
            );
        """
        )

        # if we subtract b from a we should get some drop column queries in one alter statement
        operations = a.to(b)
        self.assertEquals(1, len(operations))
        self.assertEquals(
            'ALTER TABLE `tasks` ADD `membership_id` INT(10) UNSIGNED NOT NULL AFTER `account_id`, ADD `subject` TEXT AFTER `task`;',
            str(operations[0])
        )

    def test_add_remove_change_columns(self):

        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL
            );
        """
        )

        b = CreateParser()
        b.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) NOT NULL DEFAULT 0,
            `membership_id` int(10) unsigned not null,
            `subject` text
            );
        """
        )

        # but we can ask for it in one
        operations = a.to(b)
        self.assertEquals(1, len(operations))
        self.assertEquals(
            'ALTER TABLE `tasks` ADD `membership_id` INT(10) UNSIGNED NOT NULL AFTER `account_id`, ADD `subject` TEXT AFTER `membership_id`, CHANGE `account_id` `account_id` INT(10) NOT NULL DEFAULT 0, DROP task;',
            str(operations[0])
        )

    def test_split(self):

        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL
            );
        """
        )

        b = CreateParser()
        b.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) NOT NULL DEFAULT 0,
            `membership_id` int(10) unsigned not null,
            `subject` text,
            CONSTRAINT `tasks_account_id_ref_accounts_id` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
            );
        """
        )

        operations = a.to(b, True)
        self.assertEquals(2, len(operations))
        self.assertEquals(
            'ALTER TABLE `tasks` ADD CONSTRAINT `tasks_account_id_ref_accounts_id` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;',
            str(operations['fks'])
        )
        self.assertEquals(
            'ALTER TABLE `tasks` ADD `membership_id` INT(10) UNSIGNED NOT NULL AFTER `account_id`, ADD `subject` TEXT AFTER `membership_id`, CHANGE `account_id` `account_id` INT(10) NOT NULL DEFAULT 0, DROP task;',
            str(operations['kitchen_sink'])
        )
