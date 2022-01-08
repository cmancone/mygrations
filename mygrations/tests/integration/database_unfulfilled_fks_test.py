import unittest

from mygrations.formats.mysql.file_reader.database import Database as DatabaseReader
from mygrations.formats.mysql.file_reader.create_parser import CreateParser
class DatabaseUnfulfilledFKsTest(unittest.TestCase):
    def test_can_fulfill(self):
        """ If we have all necessary columns in all necessary tables, we can fulfill the FKs """

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """, """
            CREATE TABLE `types` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `name` VARCHAR(255),
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `type_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            KEY `log_changes_type_id` (`type_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT `log_changes_type_id_fk` FOREIGN KEY (`type_id`) REFERENCES `types` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
            );
        """
        )

        self.assertEquals(0, len(db.unfulfilled_fks(new_table)))

    def test_can_not_fulfill(self):
        """ If we are missing even just one we can't fulfill and should get back the missing constraint """

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `type_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            KEY `log_changes_type_id` (`type_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT `log_changes_type_id_fk` FOREIGN KEY (`type_id`) REFERENCES `types` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_type_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_type_id_fk` FOREIGN KEY (`type_id`) REFERENCES `types` (`id`) ON DELETE CASCADE ON UPDATE CASCADE',
            str(errors_1215['log_changes_type_id_fk']['foreign_key'])
        )
        self.assertEquals(
            'Constraint error for foreign key `log_changes_type_id_fk`: `log_changes`.`type_id` references `types`.`id`, but table `types` does not exist',
            errors_1215['log_changes_type_id_fk']['error']
        )

    def test_missing_column(self):
        """ If we are missing even just one we can't fulfill and should get back the missing constraint """

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `type_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            KEY `log_changes_type_id` (`type_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT `log_changes_type_id_fk` FOREIGN KEY (`type_id`) REFERENCES `logs` (`bob`) ON DELETE CASCADE ON UPDATE CASCADE
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_type_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_type_id_fk` FOREIGN KEY (`type_id`) REFERENCES `logs` (`bob`) ON DELETE CASCADE ON UPDATE CASCADE',
            str(errors_1215['log_changes_type_id_fk']['foreign_key'])
        )
        self.assertEquals(
            'Constraint error for foreign key `log_changes_type_id_fk`: `log_changes`.`type_id` references `logs`.`bob`, but column `logs`.`bob` does not exist',
            errors_1215['log_changes_type_id_fk']['error']
        )

    def test_1215_wrong_type(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` BIGINT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_log_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE',
            str(errors_1215['log_changes_log_id_fk']['foreign_key'])
        )
        self.assertEquals(
            "Constraint error for foreign key `log_changes_log_id_fk`: column type mismatch. `log_changes`.`log_id` is 'BIGINT' but `logs`.`id` is 'INT'",
            errors_1215['log_changes_log_id_fk']['error']
        )

    def test_1215_wrong_length(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(11) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_log_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE',
            str(errors_1215['log_changes_log_id_fk']['foreign_key'])
        )
        self.assertEquals(
            "Constraint error for foreign key `log_changes_log_id_fk`: length mismatch. `log_changes`.`log_id` is '11' but `logs`.`id` is '10'",
            errors_1215['log_changes_log_id_fk']['error']
        )

    def test_1215_wrong_unsigned(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_log_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE',
            str(errors_1215['log_changes_log_id_fk']['foreign_key'])
        )
        self.assertEquals(
            "Constraint error for foreign key `log_changes_log_id_fk`: unsigned mistmatch. `logs`.`id` is unsigned but `log_changes`.`log_id` is not",
            errors_1215['log_changes_log_id_fk']['error']
        )

    def test_1215_wrong_unsigned_reversed(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_log_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE',
            str(errors_1215['log_changes_log_id_fk']['foreign_key'])
        )
        self.assertEquals(
            "Constraint error for foreign key `log_changes_log_id_fk`: unsigned mistmatch. `log_changes`.`log_id` is unsigned but `logs`.`id` is not",
            errors_1215['log_changes_log_id_fk']['error']
        )

    def test_1215_on_delete_set_null_not_nullable(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_log_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE SET NULL ON UPDATE CASCADE',
            str(errors_1215['log_changes_log_id_fk']['foreign_key'])
        )
        self.assertEquals(
            "Constraint error for foreign key `log_changes_log_id_fk`: invalid SET NULL. `log_changes`.`log_id` is not allowed to be null but the foreign key attempts to set the value to null ON DELETE",
            errors_1215['log_changes_log_id_fk']['error']
        )

    def test_1215_on_update_set_null_not_nullable(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE SET NULL,
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_log_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE SET NULL',
            str(errors_1215['log_changes_log_id_fk']['foreign_key'])
        )
        self.assertEquals(
            "Constraint error for foreign key `log_changes_log_id_fk`: invalid SET NULL. `log_changes`.`log_id` is not allowed to be null but the foreign key attempts to set the value to null ON UPDATE",
            errors_1215['log_changes_log_id_fk']['error']
        )

    def test_1215_on_update_on_delete_set_null_not_nullable(self):

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE SET NULL ON UPDATE SET NULL,
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_log_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE SET NULL ON UPDATE SET NULL',
            str(errors_1215['log_changes_log_id_fk']['foreign_key'])
        )
        self.assertEquals(
            "Constraint error for foreign key `log_changes_log_id_fk`: invalid SET NULL. `log_changes`.`log_id` is not allowed to be null but the foreign key attempts to set the value to null ON DELETE and ON UPDATE",
            errors_1215['log_changes_log_id_fk']['error']
        )

    def test_missing_index(self):
        """ If we have all necessary columns in all necessary tables, we can fulfill the FKs """

        strings = [
            """
            CREATE TABLE `logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `message` TEXT NOT NULL,
                `traceback` text
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """, """
            CREATE TABLE `types` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `name` VARCHAR(255),
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        ]
        db = DatabaseReader(strings)

        new_table = CreateParser()
        new_table.parse(
            """CREATE TABLE `log_changes` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `log_id` INT(10) UNSIGNED NOT NULL,
            `type_id` INT(10) UNSIGNED NOT NULL,
            `change` VARCHAR(255),
            PRIMARY KEY (id),
            KEY `log_changes_log_id` (`log_id`),
            KEY `log_changes_type_id` (`type_id`),
            CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT `log_changes_type_id_fk` FOREIGN KEY (`type_id`) REFERENCES `types` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
            );
        """
        )

        errors_1215 = db.unfulfilled_fks(new_table)
        self.assertEquals(1, len(errors_1215))
        self.assertTrue('log_changes_log_id_fk' in errors_1215)
        self.assertEquals(
            'CONSTRAINT `log_changes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `logs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE',
            str(errors_1215['log_changes_log_id_fk']['foreign_key'])
        )
        self.assertEquals(
            "Constraint error for foreign key `log_changes_log_id_fk`: missing index. `log_changes`.`log_id` references `logs`.`id` but `logs`.`id` does not have an index and therefore cannot be used in a foreign key constraint",
            errors_1215['log_changes_log_id_fk']['error']
        )
