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
        self.assertEquals(1, len(operations))
        self.assertEquals('ALTER TABLE `tasks` DROP KEY `tasks_account_id`, DROP KEY `task`;', str(operations[0]))

    def test_add_keys(self):
        (a, b) = self._get_parsers()

        # if we subtract b from a we should get some drop column queries in one alter statement
        operations = a.to(b)
        self.assertEquals(1, len(operations))
        self.assertEquals(
            'ALTER TABLE `tasks` ADD KEY `tasks_account_id` (`account_id`), ADD KEY `task` (`task`,`account_id`);',
            str(operations[0])
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
        self.assertEquals(1, len(operations))
        self.assertEquals(
            'ALTER TABLE `tasks` DROP KEY `tasks_account_id`, ADD KEY `tasks_account_id` (`account_id`,`id`,`task`);',
            str(operations[0])
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
        self.assertEquals(1, len(operations))
        self.assertEquals(
            'ALTER TABLE `tasks` ADD KEY `task_id` (`task`,`id`), DROP KEY `tasks_task`, DROP KEY `tasks_account_id`, ADD KEY `tasks_account_id` (`account_id`,`id`,`task`);',
            str(operations[0])
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
        self.assertEquals(1, len(operations))
        self.assertEquals(
            'ALTER TABLE `tasks` ADD UNIQUE KEY `added` (`task`), DROP KEY `uniq_task`, DROP KEY `uniq_account_id`, ADD UNIQUE KEY `uniq_account_id` (`account_id`,`id`);',
            str(operations[0])
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
        self.assertEquals(1, len(operations))
        self.assertEquals('ALTER TABLE `tasks` ADD PRIMARY KEY (`id`);', str(operations[0]))

        operations = b.to(a)
        self.assertEquals(1, len(operations))
        self.assertEquals('ALTER TABLE `tasks` DROP PRIMARY KEY;', str(operations[0]))
