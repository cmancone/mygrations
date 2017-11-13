import os
import glob

from ..file_reader.reader import reader as sql_reader
from mygrations.formats.mysql.definitions.database import database as database_definition

class database( database_definition ):

    def __init__( self, conn ):
        """ Constructor.  Accepts a mygrations db wrapper

        :param conn: mygrations db wrapper
        :type conn: mygrations.drivers.mysqldb.mysqldb
        """
        self.conn = conn
        self._warnings = []
        self._errors = []
        self._tables = {}
        self._rows = []

        # _load_tables will get the party started
        self._load_tables( self.conn )

    def _load_tables( self, conn ):
        """ Reads a database from the MySQL connection.

        Accepts a mygrations db wrapper

        :param conn: mygrations db wrapper
        :type conn: mygrations.drivers.mysqldb.mysqldb
        """
        for ( table, create_table ) in conn.tables().items():
            try:
                reader = sql_reader()
                reader.parse( create_table )

            except ValueError as e:
                print( "Error in table %s: %s" % ( create_table, e ) )

            # we shouldn't get any errors, of course, because
            # this is coming out of MySQL.  However, it may still
            # get some warnings (due to lint settings (maybe)).  Either way,
            # keep around the errors just because, even if it is
            # always empty.
            self._errors.extend( reader.errors )
            self._warnings.extend( reader.warnings )

            for (table_name,table) in reader.tables.items():
                if table.name in self._tables:
                    self.errors.append( 'Found two definitions for table %s' % table.name )

                # our reader will return table objects
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

        This object connects to the actual database.  However, we only need to know
        about the rows on a table in a minority of cases.  Mainly, whenever a table's rows
        are being managed by the mygration system.  This primarily just happens for tables
        which contain configuration information.  How do we know that a table's rows
        are being managed?  **We** don't, but the mygration system does.  If the *.sql file
        for a table has rows then the system assumes that its rows are being managed,
        and when appropriate that will prompt a call to this method which will actually
        load the rows to see if anything has changed.

        :param table: The table to read rows for
        :type table: string|mygrations.formats.mysql.definitions.table
        """
        if type( table ) != str:
            table = table.name

        if not table in self.tables:
            raise ValueError( "Cannot read rows for table %s because that table is not found in the database object" )

        for row in self.conn.rows( table ):
            self.tables[table].add_raw_row( row )

        # if the table is empty the system won't realize that we loaded rows for it
        # for bookeeping purposes, mark the table as read
        self.tables[table].mark_tracking_rows()
