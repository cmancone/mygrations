import unittest

from mygrations.formats.mysql.file_reader.create_parser import CreateParser


class CreateParserTest(unittest.TestCase):
    def test_complicated_table_parses(self):

        # parse a typical foreign key constraint
        parser = CreateParser()
        returned = parser.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `membership_id` int(10) DEFAULT NULL,
            `status_id` int(10) DEFAULT NULL,
            `priority_id` int(10) unsigned DEFAULT NULL,
            `task_type_id` int(10) unsigned DEFAULT NULL,
            `task_team_id` int(10) unsigned DEFAULT NULL,
            `repeating_tasks_id` int(10) unsigned DEFAULT NULL,
            `subject` varchar(255) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            `due_date` int(10) DEFAULT NULL,
            `original_due_date` int(10) DEFAULT NULL,
            `assigned_to_id` int(10) unsigned DEFAULT NULL,
            `delegated_to_id` int(10) DEFAULT NULL,
            `trust` tinyint(1) NOT NULL DEFAULT 0,
            `description` text,
            `multiple_task_id` int(10) DEFAULT NULL,
            `completed_dt` int(10) DEFAULT NULL,
            `duration` int(10) NOT NULL DEFAULT 0,
            `number_comments` int(10) NOT NULL DEFAULT 0,
            `number_uploads` int(10) NOT NULL DEFAULT '0',
            `created` int(10) DEFAULT NULL,
            `updated` int(10) DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `task_status_id` (`status_id`),
            KEY `task_priority_id` (`priority_id`),
            KEY `tasks_membership_id` (`membership_id`),
            KEY `task_type_id` (`task_type_id`),
            KEY `task_assigned_to_id` (`assigned_to_id`),
            CONSTRAINT `tasks_assigned_to_id_ref_memberships_user_id` FOREIGN KEY (`assigned_to_id`) REFERENCES `memberships` (`id`) ON DELETE SET NULL,
            CONSTRAINT `tasks_priority_id_ref_task_priorities_id` FOREIGN KEY (`priority_id`) REFERENCES `task_priorities` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `tasks_type_id_ref_task_types_id` FOREIGN KEY (`task_type_id`) REFERENCES `task_types` (`id`) ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        )

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have matched everything
        self.assertEqual("tasks", parser.name)
        self.assertEqual("", returned)
        self.assertEqual(23, len(parser.columns))
        self.assertEqual(6, len(parser.indexes))
        self.assertEqual(3, len(parser.constraints))
        self.assertEqual(2, len(parser.options))
        self.assertTrue(parser.semicolon)
        self.assertEqual(0, len(parser.schema_errors))
        self.assertEqual(["id"], parser.primary.columns)

    def test_keeps_errors(self):

        # parse a typical foreign key constraint
        parser = CreateParser()
        returned = parser.parse(
            """CREATE TABLE `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `subject` varchar DEFAULT NULL,
            `task` text DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        )

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some errors
        self.assertEqual(2, len(parser.schema_errors))
        self.assertEqual(
            "Column 'task' of type 'TEXT' cannot have a default in table 'tasks'",
            parser.schema_errors[0],
        )
        self.assertEqual(
            "Table 'tasks' has an AUTO_INCREMENT column but is missing the PRIMARY index",
            parser.schema_errors[1],
        )

    def test_if_not_exists_parses(self):

        # parse CREATE TABLE IF NOT EXISTS with a complicated table
        parser = CreateParser()
        returned = parser.parse(
            """CREATE TABLE IF NOT EXISTS `tasks` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `account_id` int(10) DEFAULT NULL,
            `membership_id` int(10) DEFAULT NULL,
            `status_id` int(10) DEFAULT NULL,
            `priority_id` int(10) unsigned DEFAULT NULL,
            `task_type_id` int(10) unsigned DEFAULT NULL,
            `task_team_id` int(10) unsigned DEFAULT NULL,
            `repeating_tasks_id` int(10) unsigned DEFAULT NULL,
            `subject` varchar(255) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            `due_date` int(10) DEFAULT NULL,
            `original_due_date` int(10) DEFAULT NULL,
            `assigned_to_id` int(10) unsigned DEFAULT NULL,
            `delegated_to_id` int(10) DEFAULT NULL,
            `trust` tinyint(1) NOT NULL DEFAULT 0,
            `description` text,
            `multiple_task_id` int(10) DEFAULT NULL,
            `completed_dt` int(10) DEFAULT NULL,
            `duration` int(10) NOT NULL DEFAULT 0,
            `number_comments` int(10) NOT NULL DEFAULT 0,
            `number_uploads` int(10) NOT NULL DEFAULT '0',
            `created` int(10) DEFAULT NULL,
            `updated` int(10) DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `task_status_id` (`status_id`),
            KEY `task_priority_id` (`priority_id`),
            KEY `tasks_membership_id` (`membership_id`),
            KEY `task_type_id` (`task_type_id`),
            KEY `task_assigned_to_id` (`assigned_to_id`),
            CONSTRAINT `tasks_assigned_to_id_ref_memberships_user_id` FOREIGN KEY (`assigned_to_id`) REFERENCES `memberships` (`id`) ON DELETE SET NULL,
            CONSTRAINT `tasks_priority_id_ref_task_priorities_id` FOREIGN KEY (`priority_id`) REFERENCES `task_priorities` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `tasks_type_id_ref_task_types_id` FOREIGN KEY (`task_type_id`) REFERENCES `task_types` (`id`) ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        )

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have matched everything (table name should be 'tasks', not 'IF')
        self.assertEqual("tasks", parser.name)
        self.assertEqual("", returned)
        self.assertEqual(23, len(parser.columns))
        self.assertEqual(6, len(parser.indexes))
        self.assertEqual(3, len(parser.constraints))
        self.assertEqual(2, len(parser.options))
        self.assertTrue(parser.semicolon)
        self.assertEqual(0, len(parser.schema_errors))
        self.assertEqual(["id"], parser.primary.columns)

    def test_inline_comments_stripped(self):

        parser = CreateParser()
        returned = parser.parse(
            """CREATE TABLE `test` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            -- This is a comment
            `name` varchar(255) NOT NULL,
            -- Another comment
            `status` tinyint(1) DEFAULT 0,
            PRIMARY KEY (`id`)
            );
        """
        )

        self.assertTrue(parser.matched)
        self.assertEqual("test", parser.name)
        self.assertEqual("", returned)
        self.assertEqual(3, len(parser.columns))
        self.assertIn("id", parser.columns)
        self.assertIn("name", parser.columns)
        self.assertIn("status", parser.columns)

    def test_inline_comments_at_line_end(self):

        parser = CreateParser()
        returned = parser.parse(
            """CREATE TABLE `test` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT, -- primary id
            `name` varchar(255) NOT NULL, -- user name
            PRIMARY KEY (`id`)
            );
        """
        )

        self.assertTrue(parser.matched)
        self.assertEqual("test", parser.name)
        self.assertEqual(2, len(parser.columns))
        self.assertIn("id", parser.columns)
        self.assertIn("name", parser.columns)

    def test_prefix_length_index_stripped(self):

        parser = CreateParser()
        returned = parser.parse(
            """CREATE TABLE `test` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `full_path` text NOT NULL,
            `name` varchar(255) NOT NULL,
            PRIMARY KEY (`id`),
            INDEX `idx_full_path` (`full_path`(255)),
            KEY `idx_name` (`name`(100), `id`)
            );
        """
        )

        self.assertTrue(parser.matched)
        self.assertEqual("test", parser.name)
        self.assertEqual("", returned)
        self.assertEqual(3, len(parser.columns))
        self.assertEqual(3, len(parser.indexes))
        self.assertEqual(["full_path"], parser.indexes["idx_full_path"].columns)
        self.assertEqual(["name", "id"], parser.indexes["idx_name"].columns)
        self.assertEqual("VARCHAR", parser.columns["name"].column_type)
        self.assertEqual("255", parser.columns["name"].length)

    def test_boolean_columns_with_bare_foreign_key(self):

        parser = CreateParser()
        returned = parser.parse(
            """CREATE TABLE IF NOT EXISTS project_configs (
            project_id INT UNSIGNED NOT NULL DEFAULT 0 PRIMARY KEY,
            reset_approvals_on_push BOOLEAN,
            selective_code_owner_removals BOOLEAN,
            disable_overriding_approvers_per_merge_request BOOLEAN,
            merge_requests_author_approval BOOLEAN,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
        """
        )

        self.assertTrue(parser.matched)
        self.assertEqual("project_configs", parser.name)
        self.assertEqual("", returned)
        self.assertEqual(5, len(parser.columns))
        self.assertEqual(1, len(parser.constraints))
        self.assertEqual("INT", parser.columns["project_id"].column_type)
        self.assertTrue(parser.columns["project_id"].unsigned)
        self.assertEqual("TINYINT", parser.columns["reset_approvals_on_push"].column_type)
        self.assertEqual("1", parser.columns["reset_approvals_on_push"].length)

    def test_primary_key_not_null_false_positive(self):
        """SQL file uses inline PRIMARY KEY without NOT NULL;
        SHOW CREATE TABLE always includes NOT NULL.  The two representations
        must produce identical columns so no CHANGE is emitted."""

        sql_file = """CREATE TABLE businesses (
            id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
            name varchar(255)
        )"""

        show_create = """CREATE TABLE `businesses` (
            `id` int unsigned NOT NULL AUTO_INCREMENT,
            `name` varchar(255) DEFAULT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""

        file_parser = CreateParser()
        file_parser.parse(sql_file)
        self.assertTrue(file_parser.matched)

        db_parser = CreateParser()
        db_parser.parse(show_create)
        self.assertTrue(db_parser.matched)

        file_id = file_parser.columns["id"]
        db_id = db_parser.columns["id"]

        self.assertEqual(str(file_id), str(db_id))
        self.assertTrue(file_id.is_really_the_same_as(db_id))

    def test_integer_synonym_no_false_positive_change(self):
        """SQL file uses INTEGER (MySQL synonym for INT).  SHOW CREATE TABLE
        always outputs int.  No CHANGE should be emitted."""

        sql_file = """CREATE TABLE members (
            id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
            access_level INTEGER NOT NULL DEFAULT 0,
            count INTEGER
        )"""

        show_create = """CREATE TABLE `members` (
            `id` int unsigned NOT NULL AUTO_INCREMENT,
            `access_level` int NOT NULL DEFAULT 0,
            `count` int DEFAULT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB"""

        file_parser = CreateParser()
        file_parser.parse(sql_file)
        self.assertTrue(file_parser.matched)

        db_parser = CreateParser()
        db_parser.parse(show_create)
        self.assertTrue(db_parser.matched)

        operations = db_parser.to(file_parser)
        self.assertEqual(0, len(operations))

    def test_integer_with_length_synonym_no_false_positive(self):
        """SQL file uses INTEGER(1), DB has int(1).  No CHANGE should be emitted."""

        sql_file = """CREATE TABLE settings (
            id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
            enabled INTEGER(1)
        )"""

        show_create = """CREATE TABLE `settings` (
            `id` int unsigned NOT NULL AUTO_INCREMENT,
            `enabled` int(1) DEFAULT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB"""

        file_parser = CreateParser()
        file_parser.parse(sql_file)
        self.assertTrue(file_parser.matched)

        db_parser = CreateParser()
        db_parser.parse(show_create)
        self.assertTrue(db_parser.matched)

        operations = db_parser.to(file_parser)
        self.assertEqual(0, len(operations))
