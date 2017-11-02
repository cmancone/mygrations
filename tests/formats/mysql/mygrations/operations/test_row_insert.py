import unittest
from mygrations.formats.mysql.mygrations.operations.row_insert import row_insert
from collections import OrderedDict

class test_row_insert( unittest.TestCase ):
    def test_simple( self ):
        op = row_insert( 'a_table', OrderedDict( [ ('id', 5), ('name', 'bob'), ('age', 2) ] ) )

        self.assertEquals( "INSERT INTO `a_table` (`id`, `name`, `age`) VALUES ('5', 'bob', '2');", str( op ) )
        self.assertEquals( 'a_table', op.table_name )
