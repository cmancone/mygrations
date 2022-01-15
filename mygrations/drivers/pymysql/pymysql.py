import pymysql as pymysql_driver    # alias to avoid confusion
from collections import OrderedDict
class PyMySQL(object):
    """ High level driver for a MySQLdb connection """
    execute_cursor = None

    def __init__(self, credentials=None, connection=None):
        """ Initialize the PyMySQL connection

        Accepts either a dictionary with mysql connnection credentials or a PyMySQL connection object.
        """
        if credentials is not None:
            self.connection = pymysql_driver.connect(
                user=credentials['user'],
                password=credentials['password'],
                host=credentials['host'],
                database=credentials['database'],
                autocommit=False,
                connect_timeout=2,
                cursorclass=pymysql_driver.cursors.DictCursor
            )
        elif connection is not None:
            self.connection = connection
        else:
            raise ValueError("Must provide either the database credentials or connection object")

    def tables(self):
        """ Returns the tables in the connected database

        :returns: An ordered dict with table definitions by table name
        :rtype: OrderedDict
        """
        cursor = self.connection.cursor()

        # not returning an iterator: just fetch everything.
        # I'm guessing this will be fine for any realistic database
        # size, and avoids issues of having multiple open cursors
        # at the same time.
        cursor.execute('SHOW TABLES')
        table_names = []
        for result_data in cursor:
            for table_name in result_data.values():
                table_names.append(table_name)

        definitions = OrderedDict()
        for table_name in table_names:
            cursor.execute('SHOW CREATE TABLE %s' % table_name)
            if not cursor.rowcount:
                raise ValueError("Failed to execute SHOW CREATE TABLE command on table %s" % table_name)

            result_data = cursor.fetchone()
            definitions[table_name] = result_data['Create Table']

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
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM %s' % table_name)
        rows = [row for row in cursor]
        cursor.close()

        return rows

    def execute(self, queries):
        if isinstance(queries, str):
            queries = [queries]

        cursor = self.connection.cursor()
        for query in queries:
            cursor.execute(query)
        self.connection.commit()
        cursor.close()
