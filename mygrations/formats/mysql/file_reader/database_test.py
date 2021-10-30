import unittest

from mygrations.formats.mysql.file_reader.database import Database
class DatabaseTest(unittest.TestCase):
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
            "Column 'numeric_column' has a numeric type but its default value is a string in table test_table",
            database.errors[0]
        )

    def test_duplicate_foreign_key_name(self):
        database = Database("""
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
        """)
        self.assertTrue('roles' in database.tables)
        self.assertTrue('people' in database.tables)
        self.assertEqual(1, len(database.errors))
        self.assertEqual(
            "Duplicate foreign key: foreign key named 'people_role_id_fk' exists in tables 'roles' and 'people'",
            database.errors[0]
        )

    def test_foreign_key_non_column(self):
        database = Database("""
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
        """)
        self.assertTrue('roles' in database.tables)
        self.assertTrue('people' in database.tables)
        self.assertEqual(1, len(database.errors))
        self.assertEqual(
            "Constraint error for foreign key `people_role_id_fk`: sets constraint on column `people`.`roles_id`, but this column does not exist",
            database.errors[0]
        )

    def test_missing_key_column(self):
        database = Database("""
CREATE TABLE `roles` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`)
);
        """)

        self.assertTrue('roles' in database.tables)
        self.assertEqual(1, len(database.errors))
        self.assertEqual(
            "Constraint error for foreign key `people_role_id_fk`: sets constraint on column `people`.`roles_id`, but this column does not exist",
            database.errors[0]
        )