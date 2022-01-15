import re
class DbStructure:
    """ Mock class used when working with classes which read the database structure/rows

    This handles just a few simple queries: SHOW TABLES, SHOW CREATE TABLE,
    and SELECT * FROM
    """
    def __init__(self, tables, table_rows):

        self.tables = tables
        self.table_rows = table_rows
        self.executed = False

    def cursor(self, cursor_type=None):
        """ Mock for the db `cursor` method.  Returns the equivalent of the default cursor

        cursor_type is ignored but included for consisitency with API standard

        :returns: self
        :rtype: self
        """
        return self

    def execute(self, query):
        """ Checks the query to see what is being executed and loads up the appropriate result set

        raises a ValueError if an unsupported query is found
        :returns: None
        """
        # You could imagine each query being handled by a separate object, but
        # there are only three queries we are supporting, and that is unlikely
        # to change anytime soon, so I'm going to keep this all in the same class
        normalized = re.sub(r'\s+', ' ', query).lower()
        if normalized == 'show tables':
            self._load_show_tables_result()
        elif normalized[:17] == 'show create table':
            self._load_show_create_result(normalized)
        else:
            self._load_select_all_result(normalized)

        self.executed = True
        self.iterator_index = -1

    def _load_show_tables_result(self):
        """ Loads up a result set internally to act as if a SHOW TABLES query was executed
        """
        tables = [val for val in self.tables.keys()]
        tables.sort()

        # results needs to be a list with a dictionary of table names as values (the key is ignored)
        self.results = [{table: table for table in tables}]

    def _load_show_create_result(self, query):
        """ Loads up a result set internally to act as if a SHOW CREATE TABLE query was executed

        :param query: The query being executed
        :type query: string
        """
        table_name = query.split()[-1]
        if table_name not in self.tables:
            raise ValueError(
                "Cannot mock cursor.execute for query %s because table %s was not set" % (query, table_name)
            )

        self.results = [{'Create Table': self.tables[table_name]}]

    def _load_select_all_result(self, query):
        """ Loads up a result set internally to act as if a SELECT * FROM query was executed

        :param query: The query executed
        :type query: string
        """
        m = re.match('select \* from (\S+)', query)
        if not m:
            raise ValueError(
                "Cannot mock cursor.execute for query %s because I was expecting a select query but cannot find the table name"
                % query
            )

        table_name = m.groups()[0].strip('`')
        if not table_name in self.table_rows:
            raise ValueError(
                "Cannot mock cursor.execute for query %s because table %s was not set to have any rows" %
                (query, table_name)
            )

        self.results = self.table_rows[table_name]

    def __iter__(self):
        """ Initializes iteration through the result set
        """
        return self

    def __next__(self):
        """ Returns the next result set from the iterator

        :returns: Tuple from result set
        :rtype: Tuple
        """
        return self.fetchone()

    def fetchone(self):
        """Returns the next result from the result set """
        if not self.executed:
            raise ValueError("Cannot fetch query results before executing")

        self.iterator_index += 1
        if self.iterator_index >= len(self.results):
            raise StopIteration

        return self.results[self.iterator_index]

    def fetchall(self):
        """ Returns the result set """

        return self.results

    def rowcount(self):
        """ Returns the number of results in the result set

        :returns: The number of records in the result set
        :rtype: integer
        """
        return len(self.results)

    def close(self):

        self.executed = False
