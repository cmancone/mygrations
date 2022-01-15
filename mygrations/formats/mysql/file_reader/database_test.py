import unittest

from mygrations.formats.mysql.file_reader.database import Database
class DatabaseTest(unittest.TestCase):
    def test_simple(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """, """
            CREATE TABLE `more_logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `more_messages` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        database = Database(strings)

        # our parser should have a table!
        self.assertTrue('logs' in database.tables)
        self.assertTrue('more_logs' in database.tables)

    def test_with_rows(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """, """
            INSERT INTO logs (id,message,traceback) VALUES (1,'hi','sup'),(2,'what','kay');
        """
        ]
        database = Database(strings)

        # our parser should have a table!
        self.assertTrue('logs' in database.tables)

        rows = database.tables['logs'].rows
        self.assertEquals('hi', rows['1']['message'])
        self.assertEquals('sup', rows['1']['traceback'])
        self.assertEquals('what', rows['2']['message'])
        self.assertEquals('kay', rows['2']['traceback'])

    def test_keeps_errors(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT DEFAULT '',
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        database = Database(strings)

        self.assertEquals(1, len(database.errors))
        self.assertTrue("Column 'message' of type 'TEXT' cannot have a default in table 'logs'" in database.errors[0])

    def test_check_mismatched_default_value_and_column(self):
        database = Database(
            """
CREATE TABLE `test_table` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `numeric_column` TINYINT(1) UNSIGNED NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
);
        """
        )

        self.assertTrue('test_table' in database.tables)
        self.assertEqual(1, len(database.errors))
        self.assertEqual(
            "Column 'numeric_column' of type 'TINYINT' cannot have a string value as a default in table 'test_table'",
            database.errors[0]
        )

    def test_duplicate_foreign_key_name(self):
        database = Database(
            """
CREATE TABLE `roles` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `people_id` INT(10) UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `role_people_id` (`people_id`),
  CONSTRAINT `people_role_id_fk` FOREIGN KEY (`people_id`) REFERENCES `people` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE `people` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `role_id` INT(10) UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `people_role_id` (`role_id`),
  CONSTRAINT `people_role_id_fk` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
        """
        )
        self.assertTrue('roles' in database.tables)
        self.assertTrue('people' in database.tables)
        self.assertEqual(1, len(database.errors))
        self.assertEqual(
            "Duplicate foreign key: foreign key named 'people_role_id_fk' exists in tables 'roles' and 'people'",
            database.errors[0]
        )

    def test_foreign_key_non_column(self):
        database = Database(
            """
CREATE TABLE `roles` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE `people` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `role_id` INT(10) UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `people_role_id` (`role_id`),
  CONSTRAINT `people_role_id_fk` FOREIGN KEY (`roles_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
        """
        )
        self.assertTrue('roles' in database.tables)
        self.assertTrue('people' in database.tables)
        self.assertEqual(1, len(database.errors))
        self.assertEqual(
            "Constraint error for foreign key `people_role_id_fk`: sets constraint on column `people`.`roles_id`, but this column does not exist",
            database.errors[0]
        )

    def test_missing_key_column(self):
        database = Database(
            """
CREATE TABLE `roles` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `account_id_key` (`account_id`)
);
        """
        )

        self.assertTrue('roles' in database.tables)
        self.assertEqual(1, len(database.errors))
        self.assertEqual(
            "Table 'roles' has index 'account_id_key' that references non-existent column 'account_id'",
            database.errors[0]
        )

    def test_mismatched_column(self):
        database = Database(
            """
CREATE TABLE `roles` (
    `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL DEFAULT '',
    PRIMARY KEY (`id`)
);
INSERT INTO `roles` (`id`,`name`,`description`) VALUES (1,'asdf','more');
        """
        )

        self.assertEqual(1, len(database.errors))
        self.assertEquals(
            "Insert error: insert command attempts to set column 'description' for table 'roles' but the column does not exist in the table.",
            database.errors[0]
        )
