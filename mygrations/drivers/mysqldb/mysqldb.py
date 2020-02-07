import MySQLdb
import MySQLdb.cursors

from collections import OrderedDict
class mysqldb(object):
    """ High level driver for a MySQLdb connection """
    execute_cursor = None

    def __init__(self, credentials):
        """ Initialize the MySQLdb connection

        Accepts either a dictionary with mysqldb connnection credentials
        or any MySQL database connection which implements the Python DB API spec v2.0

        :param credentials: The database credentials to connect with or a database connection
        :type credentials: dict|mygrations.helpers.db_credentials
        """
        if issubclass(type(credentials), dict):
            self.conn = MySQLdb.connect(**credentials)
        else:
            self.conn = credentials

    def tables(self):
        """ Returns the tables in the connected database

        :returns: An ordered dict with table definitions by table name
        :rtype: OrderedDict
        """
        cursor = self.conn.cursor()

        # not returning an iterator: just fetch everything.
        # I'm guessing this will be fine for any realistic database
        # size, and avoids issues of having multiple open cursors
        # at the same time.
        cursor.execute('SHOW TABLES')
        table_names = []
        for (table_name, ) in cursor:
            table_names.append(table_name)

        definitions = OrderedDict()
        for table_name in table_names:
            cursor.execute('SHOW CREATE TABLE %s' % table_name)
            if not cursor.rowcount:
                raise ValueError("Failed to execute SHOW CREATE TABLE command on table %s" % table_name)

            (tbl_name, create_table) = cursor.fetchone()
            definitions[table_name] = create_table

        cursor.close()

        return definitions

    def rows(self, table_name):
        """ Returns the rows in the table as a tuple of dicts

        :returns: The rows in the table
        :rtype: (dict)
        """

        # still sticking to full caching client-side without
        # support for memory-preserving iterators.  Given our
        # use case, I think this will be fine.  Can always change later
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM %s' % table_name)
        rows = cursor.fetchall()
        cursor.close()

        return rows

    def execute(self, queries):
        if isinstance(queries, str):
            queries = [queries]

        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        for query in queries:
            cursor.execute(query)
        self.conn.commit()
        cursor.close()
