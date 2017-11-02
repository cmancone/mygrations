import unittest
from mygrations.formats.mysql.mygrations.operations.row_update import row_update
from collections import OrderedDict

class test_row_update( unittest.TestCase ):
    def test_simple( self ):
        op = row_update( 'a_table', OrderedDict( [ ('id', 5), ('name', 'bob'), ('age', 2) ] ) )

        self.assertEquals( "UPDATE `a_table` SET `name`='bob', `age`='2' WHERE id=5;", str( op ) )
        self.assertEquals( 'a_table', op.table_name )

    def test_id_required( self ):
        with self.assertRaises( KeyError ):
            op = row_update( 'a_table', OrderedDict( [ ('name', 'bob'), ('age', 2) ] ) )
