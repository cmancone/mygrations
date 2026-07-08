import unittest

from mygrations.formats.mysql.file_reader.parsers.constraint_foreign import ConstraintForeign
class TestConstraintForeign(unittest.TestCase):
    def test_simple(self):

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        returned = parser.parse(
            'CONSTRAINT `accounts_status_id_ref_account_statuses_id` FOREIGN KEY (`status_id`) REFERENCES `account_statuses` (`id`) ON DELETE CASCADE ON UPDATE SET NULL'
        )

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have matched everything
        self.assertEqual('', returned)

        # we should have lots of data now
        self.assertEqual('accounts_status_id_ref_account_statuses_id', parser.name)
        self.assertEqual('status_id', parser.column_name)
        self.assertEqual('account_statuses', parser.foreign_table_name)
        self.assertEqual('id', parser.foreign_column_name)
        self.assertEqual('CASCADE', parser.on_delete)
        self.assertEqual('SET NULL', parser.on_update)
        self.assertFalse(parser.has_comma)
        self.assertEqual(
            'CONSTRAINT `accounts_status_id_ref_account_statuses_id` FOREIGN KEY (`status_id`) REFERENCES `account_statuses` (`id`) ON DELETE CASCADE ON UPDATE SET NULL',
            str(parser)
        )

    def test_all_deletes(self):

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE CASCADE ON UPDATE SET NULL')
        self.assertEqual('CASCADE', parser.on_delete)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE CASCADE ON UPDATE SET NULL',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE NO ACTION ON UPDATE SET NULL')
        self.assertEqual('NO ACTION', parser.on_delete)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE NO ACTION ON UPDATE SET NULL',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE RESTRICT ON UPDATE SET NULL')
        self.assertEqual('RESTRICT', parser.on_delete)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE RESTRICT ON UPDATE SET NULL',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE set default ON UPDATE SET NULL')
        self.assertEqual('SET DEFAULT', parser.on_delete)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE SET DEFAULT ON UPDATE SET NULL',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE set null ON UPDATE SET NULL')
        self.assertEqual('SET NULL', parser.on_delete)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE SET NULL ON UPDATE SET NULL',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON UPDATE SET NULL')
        self.assertEqual('RESTRICT', parser.on_delete)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE RESTRICT ON UPDATE SET NULL',
            str(parser)
        )

    def test_all_updates(self):

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE CASCADE ON UPDATE SET NULL')
        self.assertEqual('SET NULL', parser.on_update)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE CASCADE ON UPDATE SET NULL',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse(
            'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE NO ACTION ON UPDATE SET DEFAULT'
        )
        self.assertEqual('SET DEFAULT', parser.on_update)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE NO ACTION ON UPDATE SET DEFAULT',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE RESTRICT ON UPDATE CASCADE')
        self.assertEqual('CASCADE', parser.on_update)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse(
            'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE set default ON UPDATE no action'
        )
        self.assertEqual('NO ACTION', parser.on_update)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE SET DEFAULT ON UPDATE NO ACTION',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE set null ON UPDATE RESTRICT')
        self.assertEqual('RESTRICT', parser.on_update)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT',
            str(parser)
        )

        # parse a typical foreign key constraint
        parser = ConstraintForeign()
        parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE SET NULL')
        self.assertEqual('RESTRICT', parser.on_update)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT',
            str(parser)
        )

    def test_action_optional(self):

        # all actions are optional, and default to RESTRICT
        parser = ConstraintForeign()
        remaining = parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id)')

        self.assertTrue(parser.matched)
        self.assertEqual('', remaining)
        self.assertEqual('RESTRICT', parser.on_update)
        self.assertEqual('RESTRICT', parser.on_delete)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT',
            str(parser)
        )

    def test_leftovers(self):

        # anything that doesn't match should be returned as leftovers
        parser = ConstraintForeign()
        remaining = parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id), sup')

        self.assertTrue(parser.matched)
        self.assertEqual('sup', remaining)
        self.assertTrue(parser.has_comma)
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT',
            str(parser)
        )

        # even if the user forgets a comma
        parser = ConstraintForeign()
        remaining = parser.parse('CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) sup')
        self.assertEqual(
            'CONSTRAINT `blah` FOREIGN KEY (`check`) REFERENCES `tbl` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT',
            str(parser)
        )

        self.assertTrue(parser.matched)
        self.assertEqual('sup', remaining)
        self.assertFalse(parser.has_comma)
