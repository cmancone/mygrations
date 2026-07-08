import unittest

from mygrations.formats.mysql.file_reader.database import Database as DatabaseReader
from mygrations.formats.mysql.mygrations.mygration import Mygration


class test_fk_column_type_change(unittest.TestCase):
    parent_table_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    parent_table_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    child_table_signed = """CREATE TABLE `company_domains` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    child_table_unsigned = """CREATE TABLE `company_domains` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    def test_signed_to_unsigned_drops_and_readds_fk(self):
        """Changing INT to INT UNSIGNED on FK columns should DROP FK before ALTER and ADD FK after"""
        db_from = DatabaseReader([self.parent_table_signed, self.child_table_signed])
        db_to = DatabaseReader([self.parent_table_unsigned, self.child_table_unsigned])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        self.assertEqual("SET FOREIGN_KEY_CHECKS=0;", ops[0])
        self.assertIn("DROP FOREIGN KEY `company_domains_business_id_fk`", ops[1])
        self.assertTrue(any("CHANGE" in op for op in ops), "Expected a CHANGE column operation")
        self.assertIn(
            "ADD CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE",
            ops[-2],
        )
        self.assertEqual("SET FOREIGN_KEY_CHECKS=1;", ops[-1])

    def test_no_fk_cycle_when_types_match(self):
        """No extra DROP/ADD FK when column types are already the same"""
        db_from = DatabaseReader([self.parent_table_unsigned, self.child_table_unsigned])
        db_to = DatabaseReader([self.parent_table_unsigned, self.child_table_unsigned])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        all_ops_str = " ".join(ops)
        self.assertNotIn("DROP FOREIGN KEY", all_ops_str)
        self.assertNotIn("ADD CONSTRAINT", all_ops_str)

    def test_parent_type_change_cycles_child_fk(self):
        """Changing the parent column type should also cycle the child's FK"""
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_unsigned = """CREATE TABLE `company_domains` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_unsigned])
        db_to = DatabaseReader([parent_unsigned, child_unsigned])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        self.assertEqual("SET FOREIGN_KEY_CHECKS=0;", ops[0])
        self.assertIn("DROP FOREIGN KEY `company_domains_business_id_fk`", ops[1])
        self.assertTrue(any("CHANGE" in op or "MODIFY" in op for op in ops))
        self.assertIn(
            "ADD CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE",
            ops[-2],
        )
        self.assertEqual("SET FOREIGN_KEY_CHECKS=1;", ops[-1])

    def test_fk_definition_change_with_type_change_no_duplicates(self):
        """When both FK definition and column type change, no duplicate DROP/ADD FK"""
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_signed_cascade = """CREATE TABLE `company_domains` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_unsigned_restrict = """CREATE TABLE `company_domains` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_signed_cascade])
        db_to = DatabaseReader([parent_unsigned, child_unsigned_restrict])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        drop_fk_count = sum(1 for op in ops if "DROP FOREIGN KEY `company_domains_business_id_fk`" in op)
        add_fk_count = sum(1 for op in ops if "ADD CONSTRAINT `company_domains_business_id_fk`" in op)

        self.assertEqual(1, drop_fk_count, f"Expected exactly 1 DROP FK, got {drop_fk_count}. Operations: {ops}")
        self.assertEqual(1, add_fk_count, f"Expected exactly 1 ADD FK, got {add_fk_count}. Operations: {ops}")
        self.assertIn("ON DELETE RESTRICT", ops[-2])

    def test_multiple_fks_on_same_parent(self):
        """Multiple child tables referencing the same parent column that changes type"""
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child1 = """CREATE TABLE `company_domains` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `bd_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child2 = """CREATE TABLE `company_users` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`user_name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `bu_business_id_idx` (`business_id`),
CONSTRAINT `bu_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child1, child2])
        db_to = DatabaseReader([parent_unsigned, child1, child2])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        all_ops_str = " ".join(ops)
        self.assertIn("DROP FOREIGN KEY `bd_business_id_fk`", all_ops_str)
        self.assertIn("DROP FOREIGN KEY `bu_business_id_fk`", all_ops_str)
        self.assertIn("ADD CONSTRAINT `bd_business_id_fk`", all_ops_str)
        self.assertIn("ADD CONSTRAINT `bu_business_id_fk`", all_ops_str)

    def test_unrelated_column_change_no_fk_cycle(self):
        """Changing a non-FK column should NOT trigger FK cycling"""
        parent = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_before = """CREATE TABLE `company_domains` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_after = """CREATE TABLE `company_domains` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`domain` VARCHAR(512) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent, child_before])
        db_to = DatabaseReader([parent, child_after])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        all_ops_str = " ".join(ops)
        self.assertNotIn("DROP FOREIGN KEY", all_ops_str)
        self.assertNotIn("ADD CONSTRAINT", all_ops_str)
        self.assertTrue(any("CHANGE" in op for op in ops))

    def test_cross_table_fk_additions_deferred_after_all_column_changes(self):
        """FK additions must happen after ALL tables have column changes applied.

        Regression test for MySQL 3780 cross-table ordering: when company_domains
        (alphabetically first) has a new FK referencing businesses.id, and businesses.id
        is changing from INT to INT UNSIGNED, the ADD CONSTRAINT must not be in the same
        ALTER as company_domains' column changes — it must come after businesses' ALTER.
        """
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_signed_no_fk = """CREATE TABLE `company_domains` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_unsigned_with_fk = """CREATE TABLE `company_domains` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_signed_no_fk])
        db_to = DatabaseReader([parent_unsigned, child_unsigned_with_fk])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        change_ops = [i for i, op in enumerate(ops) if "CHANGE" in op]
        add_fk_ops = [i for i, op in enumerate(ops) if "ADD CONSTRAINT" in op]

        self.assertTrue(change_ops, "Expected CHANGE column operations")
        self.assertTrue(add_fk_ops, "Expected ADD CONSTRAINT operations")

        last_change = max(change_ops)
        first_add_fk = min(add_fk_ops)
        self.assertGreater(
            first_add_fk,
            last_change,
            f"ADD CONSTRAINT (index {first_add_fk}) must come after all CHANGE ops (last at {last_change}). Operations: {ops}",
        )

    def test_cross_table_existing_fk_with_type_change_deferred(self):
        """Existing FK that needs cycling: DROP FK before changes, ADD FK after ALL changes.

        When both tables change column types and the FK already exists, the DROP FK
        must precede all column changes, and the ADD FK must follow all column changes.
        """
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_signed = """CREATE TABLE `company_domains` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_unsigned = """CREATE TABLE `company_domains` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL,
`domain` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `company_domains_business_id_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_signed])
        db_to = DatabaseReader([parent_unsigned, child_unsigned])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        drop_fk_indices = [i for i, op in enumerate(ops) if "DROP FOREIGN KEY" in op]
        change_indices = [i for i, op in enumerate(ops) if "CHANGE" in op]
        add_fk_indices = [i for i, op in enumerate(ops) if "ADD CONSTRAINT" in op]

        self.assertTrue(drop_fk_indices, "Expected DROP FOREIGN KEY")
        self.assertTrue(change_indices, "Expected CHANGE column operations")
        self.assertTrue(add_fk_indices, "Expected ADD CONSTRAINT")

        self.assertLess(
            max(drop_fk_indices),
            min(change_indices),
            f"All DROP FK must precede all CHANGE ops. Ops: {ops}",
        )
        self.assertGreater(
            min(add_fk_indices),
            max(change_indices),
            f"All ADD FK must follow all CHANGE ops. Ops: {ops}",
        )

    def test_fk_name_mismatch_cycles_correctly(self):
        """FK with different names in source vs target should still be cycled for type changes.

        Reproduces the child_records_ibfk_1 vs business_id_businesses_fk scenario:
        MySQL auto-names bare FOREIGN KEY as 'table_ibfk_N', while SQL files generate
        'column_table_fk'.  The cycle must DROP the source-named FK and ADD the target-named FK.
        """
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_signed_ibfk = """CREATE TABLE `child_records` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL DEFAULT 0,
PRIMARY KEY (`id`),
KEY `idx_business_id` (`business_id`),
CONSTRAINT `child_records_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_unsigned_named = """CREATE TABLE `child_records` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL DEFAULT 0,
PRIMARY KEY (`id`),
KEY `idx_business_id` (`business_id`),
CONSTRAINT `business_id_businesses_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_signed_ibfk])
        db_to = DatabaseReader([parent_unsigned, child_unsigned_named])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        all_ops_str = " ".join(ops)
        self.assertIn("DROP FOREIGN KEY `child_records_ibfk_1`", all_ops_str)
        self.assertIn("ADD CONSTRAINT `business_id_businesses_fk`", all_ops_str)

    def test_duplicate_source_fks_produce_single_add(self):
        """Multiple source FKs (ibfk_1..ibfk_N) on same column should DROP all but ADD target only once.

        When MySQL accumulates duplicate auto-named FKs (e.g. from failed migrations),
        the live DB may have ibfk_1, ibfk_2, ibfk_3 all pointing to the same column/table.
        All must be DROPped, but the single target FK should be ADDed exactly once.
        """
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_with_3_duplicate_ibfks = """CREATE TABLE `child_records` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL DEFAULT 0,
PRIMARY KEY (`id`),
KEY `idx_business_id` (`business_id`),
CONSTRAINT `child_records_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE,
CONSTRAINT `child_records_ibfk_2` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE,
CONSTRAINT `child_records_ibfk_3` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_target = """CREATE TABLE `child_records` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL DEFAULT 0,
PRIMARY KEY (`id`),
KEY `idx_business_id` (`business_id`),
CONSTRAINT `business_id_businesses_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_with_3_duplicate_ibfks])
        db_to = DatabaseReader([parent_unsigned, child_target])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        all_ops_str = " ".join(ops)
        self.assertIn("DROP FOREIGN KEY `child_records_ibfk_1`", all_ops_str)
        self.assertIn("DROP FOREIGN KEY `child_records_ibfk_2`", all_ops_str)
        self.assertIn("DROP FOREIGN KEY `child_records_ibfk_3`", all_ops_str)

        add_count = sum(1 for op in ops if "ADD CONSTRAINT `business_id_businesses_fk`" in op)
        self.assertEqual(1, add_count, f"Expected exactly 1 ADD CONSTRAINT, got {add_count}. Ops: {ops}")

    def test_fk_name_mismatch_no_duplicate_ops(self):
        """When FK names differ between source/target, no duplicate DROP/ADD emitted.

        table.to() will see the old-named FK as removed and new-named FK as added.
        _find_fk_ops_for_column_type_changes() also emits DROP old / ADD new.
        _strip_cycled_fk_ops() must suppress both duplicates.
        """
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_signed_ibfk = """CREATE TABLE `child_records` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL DEFAULT 0,
PRIMARY KEY (`id`),
KEY `idx_business_id` (`business_id`),
CONSTRAINT `child_records_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_unsigned_named = """CREATE TABLE `child_records` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL DEFAULT 0,
PRIMARY KEY (`id`),
KEY `idx_business_id` (`business_id`),
CONSTRAINT `business_id_businesses_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_signed_ibfk])
        db_to = DatabaseReader([parent_unsigned, child_unsigned_named])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        drop_old_count = sum(1 for op in ops if "DROP FOREIGN KEY `child_records_ibfk_1`" in op)
        add_new_count = sum(1 for op in ops if "ADD CONSTRAINT `business_id_businesses_fk`" in op)

        self.assertEqual(1, drop_old_count, f"Expected exactly 1 DROP old FK, got {drop_old_count}. Ops: {ops}")
        self.assertEqual(1, add_new_count, f"Expected exactly 1 ADD new FK, got {add_new_count}. Ops: {ops}")

    def test_fk_name_mismatch_parent_only_change(self):
        """FK name mismatch where only the parent column changes type.

        Child table (child_records) has no column type change — only the parent
        (businesses.id) changes from INT to INT UNSIGNED.  The child's FK must still
        be cycled because the referenced column type is changing.
        """
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_unsigned_ibfk = """CREATE TABLE `child_records` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL DEFAULT 0,
PRIMARY KEY (`id`),
KEY `idx_business_id` (`business_id`),
CONSTRAINT `child_records_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_unsigned_named = """CREATE TABLE `child_records` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`business_id` INT(10) UNSIGNED NOT NULL DEFAULT 0,
PRIMARY KEY (`id`),
KEY `idx_business_id` (`business_id`),
CONSTRAINT `business_id_businesses_fk` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_unsigned_ibfk])
        db_to = DatabaseReader([parent_unsigned, child_unsigned_named])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        all_ops_str = " ".join(ops)
        self.assertIn("DROP FOREIGN KEY `child_records_ibfk_1`", all_ops_str)
        self.assertIn("ADD CONSTRAINT `business_id_businesses_fk`", all_ops_str)

    def test_table_being_dropped_with_fk_to_changing_column(self):
        parent_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_to_drop = """CREATE TABLE `old_child` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL,
PRIMARY KEY (`id`),
KEY `business_id_idx` (`business_id`),
CONSTRAINT `old_child_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent_signed, child_to_drop])
        db_to = DatabaseReader([parent_unsigned])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        all_ops_str = " ".join(ops)
        self.assertIn("DROP FOREIGN KEY `old_child_ibfk_1`", all_ops_str)
        self.assertNotIn("ADD CONSTRAINT `old_child_ibfk_1`", all_ops_str)

        drop_fk_indices = [i for i, op in enumerate(ops) if "DROP FOREIGN KEY `old_child_ibfk_1`" in op]
        change_indices = [i for i, op in enumerate(ops) if "CHANGE" in op]
        drop_table_indices = [i for i, op in enumerate(ops) if "DROP TABLE" in op]

        self.assertTrue(drop_fk_indices, "Expected DROP FK for old_child")
        self.assertTrue(change_indices, "Expected CHANGE on businesses.id")
        self.assertTrue(drop_table_indices, "Expected DROP TABLE old_child")

        self.assertLess(
            max(drop_fk_indices),
            min(change_indices),
            f"DROP FK must precede column changes. Ops: {ops}",
        )

    def test_table_being_dropped_multiple_fks_to_changing_columns(self):
        parent1_signed = """CREATE TABLE `businesses` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent1_unsigned = """CREATE TABLE `businesses` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent2_signed = """CREATE TABLE `services` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`label` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        parent2_unsigned = """CREATE TABLE `services` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`label` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        child_to_drop = """CREATE TABLE `old_junction` (`id` INT(10) NOT NULL AUTO_INCREMENT,
`business_id` INT(10) NOT NULL,
`service_id` INT(10) NOT NULL,
PRIMARY KEY (`id`),
KEY `biz_idx` (`business_id`),
KEY `svc_idx` (`service_id`),
CONSTRAINT `old_junction_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE,
CONSTRAINT `old_junction_ibfk_2` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db_from = DatabaseReader([parent1_signed, parent2_signed, child_to_drop])
        db_to = DatabaseReader([parent1_unsigned, parent2_unsigned])

        mygrate = Mygration(db_to, db_from)
        ops = [str(op) for op in mygrate.operations]

        all_ops_str = " ".join(ops)
        self.assertIn("DROP FOREIGN KEY `old_junction_ibfk_1`", all_ops_str)
        self.assertIn("DROP FOREIGN KEY `old_junction_ibfk_2`", all_ops_str)
        self.assertNotIn("ADD CONSTRAINT `old_junction_ibfk_1`", all_ops_str)
        self.assertNotIn("ADD CONSTRAINT `old_junction_ibfk_2`", all_ops_str)
