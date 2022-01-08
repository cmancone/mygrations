import unittest

from mygrations.formats.mysql.file_reader.create_parser import CreateParser
class TableDifferenceTest(unittest.TestCase):
    def test_simple_create(self):
        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id)
            );
        """
        )

        self.assertEquals(
            str(a).replace("\n", ' '),
            "CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT, `account_id` INT(10), `task` VARCHAR(255), PRIMARY KEY (`id`));"
        )

    def test_with_constraints(self):
        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            PRIMARY KEY (id),
            CONSTRAINT `tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
            );
        """
        )

        self.assertEquals(
            str(a).replace("\n", ' '),
            "CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT, `account_id` INT(10), PRIMARY KEY (`id`), CONSTRAINT `tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT);"
        )

    def test_with_options(self):
        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        )

        self.assertEquals(
            str(a).replace("\n", ' '),
            "CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT, `account_id` INT(10), `task` VARCHAR(255), PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        )
