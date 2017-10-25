import os
import glob

from ..file_reader.reader import reader as sql_reader
from mygrations.formats.mysql.definitions.database import database as database_definition

class database( database_definition ):

    def __init__( self, conn ):
        """ Constructor.  Accepts a MySQL database connection which implements the Python DB API spec v2.0

        :param conn: Any MySQL database connection compaitible with PEP 249
        :type conn: connection object
        """
        self.conn = conn
        self._warnings = []
        self._errors = []
        self._tables = {}
        self._rows = []

        # dict cursor is used for fetching rows.  Default cursor is used for pretty much everything else
        self.process( self.conn )

    def process( self, conn ):
        """ Reads a database from the MySQL connection.

        Accepts a MySQL database connection which implements the Python DB API spec v2.0

        :param conn: Any MySQL database connection compaitible with PEP 249
        :type conn: connection object
        """

        cursor = conn.cursor()
        # grab the table names out in the first pass
        # so we don't have to worry about multiple
        # concurrent queries on our cursor (and so we
        # don't have to open two cursors)
        cursor.execute( 'SHOW TABLES' )
        table_names = []
        for (table_name,) in cursor:
            table_names.append( table_name )

        for table_name in table_names:
            self._process_table( cursor, table_name )

        cursor.close()

    def _process_table( self, cursor, table_name ):
        """ Reads the table definition from the database and processes it

        Stores a table_definition for the table in this database object.  It does
        Not read/process/store any information about rows in the table.  That
        step is performed separately, only when needed.

        :param cursor: The MySQL connection cursor object
        :param table_name: The table name
        :type cursor: A MySQL connection cursor object
        :type table_name: string
        """

        cursor.execute( 'SHOW CREATE TABLE %s' % table_name )
        if not cursor.rowcount:
            raise ValueError( "Failed to execute SHOW CREATE TABLE command on table %s" % table_name )

        ( tbl_name, create_table ) = cursor.fetchone()

        try:
            reader = sql_reader()
            reader.parse( create_table )

        except ValueError as e:
            print( "Error in file %s: %s" % ( contents, e ) )

        # we shouldn't get any errors, of course, because
        # this is coming out of MySQL.  However, it may still
        # get some warnings (due to lint settings).  Either way,
        # keep around the errors just because, even if it is
        # always empty.
        self._errors.extend( reader.errors )
        self._warnings.extend( reader.warnings )

        for (table_name,table) in reader.tables.items():
            if table.name in self._tables:
                self.errors.append( 'Found two definitions for table %s' % table.name )

            # our reader will return objects table objects
            # from the file_reader namespace.  These expect
            # rows to come up inside the SQL that we pass in.
            # However, we don't have any inserts in our SQL.  Nor
            # do I want to just load up all rows and pass them
            # in for storage, because only a small minority of tables
            # will actually be tracking database rows.  Instead
            # I will sort out table records later
            self._tables[table.name] = table

    def read_rows( self, table ):
        """ Extracts the rows for the table from the database and stores them in the table object

        :param table: The table to read rows for
        :type table: string|mygrations.formats.mysql.definitions.table
        """
        if type( table ) != str:
            table = table.name

        if not table.name in self.tables:
            raise ValueError( "Cannot read rows for table %s because that table is not found in the database object" )

        cursor = conn.cursor()

        cursor.execute( 'SELECT * FROM %s ORDER BY id ASC' % table )

        cursor.close()

