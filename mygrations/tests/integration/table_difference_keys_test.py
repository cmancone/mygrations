import unittest

from mygrations.formats.mysql.file_reader.create_parser import CreateParser


class TableDifferenceKeysTest(unittest.TestCase):
    def _get_parsers(self):
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

        b = CreateParser()
        b.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id),
            KEY tasks_account_id (account_id),
            KEY task (task,account_id)
            );
        """
        )

        return (a, b)

    def test_drop_keys(self):
        (a, b) = self._get_parsers()

        # if we subtract b from a we should get some drop column queries in one alter statement
        operations = b.to(a)
        self.assertEqual(1, len(operations))
        self.assertEqual("ALTER TABLE `tasks` DROP KEY `tasks_account_id`, DROP KEY `task`;", str(operations[0]))

    def test_add_keys(self):
        (a, b) = self._get_parsers()

        # if we subtract b from a we should get some drop column queries in one alter statement
        operations = a.to(b)
        self.assertEqual(1, len(operations))
        self.assertEqual(
            "ALTER TABLE `tasks` ADD KEY `tasks_account_id` (`account_id`), ADD KEY `task` (`task`,`account_id`);",
            str(operations[0]),
        )

    def test_change_keys(self):
        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id),
            KEY tasks_account_id (account_id)
            );
        """
        )

        b = CreateParser()
        b.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id),
            KEY tasks_account_id (account_id,id,task)
            );
        """
        )

        # if we subtract b from a we should get some drop column queries in one alter statement
        operations = a.to(b)
        self.assertEqual(1, len(operations))
        self.assertEqual(
            "ALTER TABLE `tasks` DROP KEY `tasks_account_id`, ADD KEY `tasks_account_id` (`account_id`,`id`,`task`);",
            str(operations[0]),
        )

    def test_add_remove_change(self):
        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id),
            KEY unchanged (task),
            KEY tasks_task (task),
            KEY tasks_account_id (account_id)
            );
        """
        )

        b = CreateParser()
        b.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id),
            KEY unchanged (task),
            KEY task_id (task,id),
            KEY tasks_account_id (account_id,id,task)
            );
        """
        )

        # if we subtract b from a we should get some drop column queries in one alter statement
        operations = a.to(b)
        self.assertEqual(1, len(operations))
        self.assertEqual(
            "ALTER TABLE `tasks` ADD KEY `task_id` (`task`,`id`), DROP KEY `tasks_task`, DROP KEY `tasks_account_id`, ADD KEY `tasks_account_id` (`account_id`,`id`,`task`);",
            str(operations[0]),
        )

    def test_unique_keys(self):
        a = CreateParser()
        a.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY unchanged (account_id),
            UNIQUE KEY uniq_account_id (account_id),
            unique key uniq_task (task)
            );
        """
        )

        b = CreateParser()
        b.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY unchanged (account_id),
            UNIQUE KEY uniq_account_id (account_id,id),
            unique key added (task)
            );
        """
        )

        operations = a.to(b)
        self.assertEqual(1, len(operations))
        self.assertEqual(
            "ALTER TABLE `tasks` ADD UNIQUE KEY `added` (`task`), DROP KEY `uniq_task`, DROP KEY `uniq_account_id`, ADD UNIQUE KEY `uniq_account_id` (`account_id`,`id`);",
            str(operations[0]),
        )

    def test_primary_key(self):
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
            `task` varchar(255) DEFAULT NULL,
            PRIMARY KEY (id)
            );
        """
        )

        operations = a.to(b)
        self.assertEqual(1, len(operations))
        self.assertEqual("ALTER TABLE `tasks` ADD PRIMARY KEY (`id`);", str(operations[0]))

        operations = b.to(a)
        self.assertEqual(1, len(operations))
        self.assertEqual("ALTER TABLE `tasks` DROP PRIMARY KEY;", str(operations[0]))

    def test_fk_auto_index_name_mismatch_suppressed(self):
        """DB has an index auto-named after a FK constraint; SQL file defines the
        same index with a shorter name.  No ADD/DROP should be emitted."""

        db = CreateParser()
        db.parse(
            """CREATE TABLE `orders` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `user_id` int(10) unsigned DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `orders_user_id_users_fk` (`user_id`),
            CONSTRAINT `orders_user_id_users_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
            ) ENGINE=InnoDB;
        """
        )

        sql_file = CreateParser()
        sql_file.parse(
            """CREATE TABLE `orders` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `user_id` int(10) unsigned DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `user_id` (`user_id`),
            CONSTRAINT `orders_user_id_users_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
            ) ENGINE=InnoDB;
        """
        )

        operations = db.to(sql_file)
        self.assertEqual(0, len(operations))

    def test_non_fk_index_rename_not_suppressed(self):
        """When neither index name matches a constraint, the ADD/DROP must still
        be emitted — this is a legitimate rename."""

        a = CreateParser()
        a.parse(
            """CREATE TABLE `orders` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `user_id` int(10) unsigned DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `old_name` (`user_id`)
            ) ENGINE=InnoDB;
        """
        )

        b = CreateParser()
        b.parse(
            """CREATE TABLE `orders` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `user_id` int(10) unsigned DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `new_name` (`user_id`)
            ) ENGINE=InnoDB;
        """
        )

        operations = a.to(b)
        self.assertEqual(1, len(operations))
        self.assertIn("ADD KEY", str(operations[0]))
        self.assertIn("DROP KEY", str(operations[0]))

    def test_unnamed_unique_key_matches_named_unique_key(self):
        """SQL file defines UNIQUE(col1, col2) with no name; DB has
        UNIQUE KEY `col1` (col1, col2) with an explicit name.  Both resolve
        to the same key name via the first-column fallback so they overlap.
        No CHANGE should be emitted because columns and type are identical."""

        db = CreateParser()
        db.parse(
            """CREATE TABLE `members` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `group_id` int(10) unsigned DEFAULT NULL,
            `user_id` int(10) unsigned DEFAULT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `group_id` (`group_id`,`user_id`)
            ) ENGINE=InnoDB;
        """
        )

        sql_file = CreateParser()
        sql_file.parse(
            """CREATE TABLE `members` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `group_id` int(10) unsigned DEFAULT NULL,
            `user_id` int(10) unsigned DEFAULT NULL,
            PRIMARY KEY (`id`),
            UNIQUE(`group_id`,`user_id`)
            ) ENGINE=InnoDB;
        """
        )

        operations = db.to(sql_file)
        self.assertEqual(0, len(operations))
