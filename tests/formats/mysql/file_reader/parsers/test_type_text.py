import unittest

from mygrations.formats.mysql.file_reader.parsers.type_text import type_text

class test_type_text( unittest.TestCase ):

    def test_simple( self ):

        # parse typical insert values
        parser = type_text()
        returned = parser.parse( "name text not null," )

        self.assertTrue( parser.matched )
        self.assertEquals( '', returned )

        self.assertEquals( 'column', parser.definition_type )
        self.assertEquals( 'name', parser.name )
        self.assertEquals( 'TEXT', parser.column_type )
        self.assertFalse( parser.null )
        self.assertTrue( parser.has_comma )
        self.assertEquals( '', parser.character_set )
        self.assertEquals( '', parser.collate )
        self.assertEquals( 0, len( parser.errors ) )
        self.assertEquals( "`name` TEXT NOT NULL", str(parser) )

    def test_character_set( self ):

        # parse typical insert values
        parser = type_text()
        returned = parser.parse( "name text character set 'blah' collate 'boo'," )

        self.assertTrue( parser.matched )
        self.assertEquals( '', returned )

        self.assertEquals( 'column', parser.definition_type )
        self.assertEquals( 'name', parser.name )
        self.assertEquals( 'TEXT', parser.column_type )
        self.assertTrue( parser.null )
        self.assertTrue( parser.has_comma )
        self.assertEquals( 'BLAH', parser.character_set )
        self.assertEquals( 'BOO', parser.collate )
        self.assertEquals( 0, len( parser.errors ) )
        self.assertEquals( "`name` TEXT CHARACTER SET 'BLAH' COLLATE 'BOO'", str(parser) )

    def test_strip_backticks( self ):

        # parse typical insert values
        parser = type_text()
        returned = parser.parse( "`name` text not null" )

        self.assertTrue( parser.matched )
        self.assertEquals( '', returned )
        self.assertEquals( 'column', parser.definition_type )
        self.assertEquals( 'name', parser.name )
        self.assertEquals( "`name` TEXT NOT NULL", str(parser) )

    def test_no_default( self ):

        # parse typical insert values
        parser = type_text()
        returned = parser.parse( "name text default 'bob'" )

        self.assertTrue( parser.matched )
        self.assertEquals( '', returned )
        self.assertTrue( 'not allowed to have a default' in parser.errors[0] )

    # some types must have a length
    def test_invalid_column_type( self ):

        for coltype in [ 'integer', 'varchar', 'afijeirjeri' ]:

            parser = type_text()
            returned = parser.parse( 'name %s' % coltype )

            self.assertTrue( parser.matched )
            self.assertEquals( '', returned )
            self.assertTrue( 'must have a length' in parser.errors[0] )

    # only some types can not have a length
    def test_valid_column_type( self ):

        for coltype in [ 'tinyblob', 'blob', 'mediumblob', 'longblob', 'tinytext', 'text', 'mediumtext', 'longtext' ]:

            parser = type_text()
            returned = parser.parse( 'name %s' % coltype )

            self.assertTrue( parser.matched )
            self.assertEquals( '', returned )
            self.assertEquals( 0, len( parser.errors ) )
