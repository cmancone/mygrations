import unittest

from mygrations.formats.mysql.file_reader.parsers.constraint_foreign import constraint_foreign

class test_constraint_foreign( unittest.TestCase ):

    def test_simple( self ):

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        returned = parser.parse( 'CONSTRAINT `accounts_status_id_ref_account_statuses_id` FOREIGN KEY (`status_id`) REFERENCES `account_statuses` (`id`) ON DELETE CASCADE ON UPDATE SET NULL' )

        # we should have matched
        self.assertTrue( parser.matched )

        # and we should have matched everything
        self.assertEquals( '', returned )

        # we should have lots of data now
        self.assertEquals( 'accounts_status_id_ref_account_statuses_id', parser.name )
        self.assertEquals( 'status_id', parser.column )
        self.assertEquals( 'account_statuses', parser.foreign_table )
        self.assertEquals( 'id', parser.foreign_column )
        self.assertEquals( 'CASCADE', parser.on_delete )
        self.assertEquals( 'SET NULL', parser.on_update )
        self.assertFalse( parser.has_comma )
        self.assertEquals( parser.definition_type, 'constraint' )

    def test_all_deletes( self ):

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE CASCADE ON UPDATE SET NULL' )
        self.assertEquals( 'CASCADE', parser.on_delete )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE NO ACTION ON UPDATE SET NULL' )
        self.assertEquals( 'NO ACTION', parser.on_delete )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE RESTRICT ON UPDATE SET NULL' )
        self.assertEquals( 'RESTRICT', parser.on_delete )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE set default ON UPDATE SET NULL' )
        self.assertEquals( 'SET DEFAULT', parser.on_delete )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE set null ON UPDATE SET NULL' )
        self.assertEquals( 'SET NULL', parser.on_delete )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON UPDATE SET NULL' )
        self.assertEquals( 'RESTRICT', parser.on_delete )

    def test_all_updates( self ):

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE CASCADE ON UPDATE SET NULL' )
        self.assertEquals( 'SET NULL', parser.on_update )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE NO ACTION ON UPDATE SET DEFAULT' )
        self.assertEquals( 'SET DEFAULT', parser.on_update )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE RESTRICT ON UPDATE CASCADE' )
        self.assertEquals( 'CASCADE', parser.on_update )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE set default ON UPDATE no action' )
        self.assertEquals( 'NO ACTION', parser.on_update )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE set null ON UPDATE RESTRICT' )
        self.assertEquals( 'RESTRICT', parser.on_update )

        # parse a typical foreign key constraint
        parser = constraint_foreign()
        parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) ON DELETE SET NULL' )
        self.assertEquals( 'RESTRICT', parser.on_update )

    def test_action_optional( self ):

        # all actions are optional, and default to RESTRICT
        parser = constraint_foreign()
        remaining = parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id)' )

        self.assertTrue( parser.matched )
        self.assertEquals( '', remaining )
        self.assertEquals( 'RESTRICT', parser.on_update )
        self.assertEquals( 'RESTRICT', parser.on_delete )

    def test_leftovers( self ):

        # anything that doesn't match should be returned as leftovers
        parser = constraint_foreign()
        remaining = parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id), sup' )

        self.assertTrue( parser.matched )
        self.assertEquals( 'sup', remaining )
        self.assertTrue( parser.has_comma )

        # even if the user forgets a comma
        parser = constraint_foreign()
        remaining = parser.parse( 'CONSTRAINT blah FOREIGN KEY (check) REFERENCES tbl (id) sup' )

        self.assertTrue( parser.matched )
        self.assertEquals( 'sup', remaining )
        self.assertFalse( parser.has_comma )
