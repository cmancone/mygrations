from mygrations.core.parse.parser import Parser
class CommentParser(Parser):

    rules = ['nope']
    sql = ''

    def __init__(self, rules=[]):

        # we're not yet a rules-based parser (I may do that eventually), so
        # I don't want to run the normal parser __init__()
        self.matched = False
        self._parsing_errors = []
        self._parsing_warnings = []
        self._schema_errors = []
        self._schema_warnings = []

    def parse(self, sql):
        """ res = paser.parse()

        Parses the SQL, storing the comment and returning an SQL string with the comment removed

        :param sql: The SQL string to parse
        :type sql: string
        :returns: The SQL string with the first comment removed
        :rtype: string

        :Example:
                >>> import comment_parser
                >>> parser = comment_parser( '--Some SQL\nINSERT INTO some_table (1,2)' )
                >>> without_comment = parser.parse()
                >>> print( parser.comment )
                Some SQL
                >>> print( without_comment )
                INSERT INTO some_table (1,2)
        """

        self.sql = sql.strip()
        self.comment = ''

        # what kind of comment are we dealing with?
        # -- and # go to the end of the line.  /* goes to */
        if self.sql[0] == '#' or self.sql[:2] == '--':

            # which is really easy if there is no newline: the
            # whole thing is our comment and there is no data left
            if not self.sql.count('\n'):
                self.comment = self.sql
                self._values = {'commment': self.comment}
                self.matched = True
                return ''

            # otherwise just find the newline and return the rest
            else:
                index = self.sql.index('\n')
                self.comment = self.sql[:index]
                self._values = {'commment': self.comment}
                self.matched = True
                return self.sql[index + 1:].strip()

        # then we should be dealing with /* ... */.  Our line should
        # start with it or we have a problem
        if self.sql[:2] != '/*':
            raise ValueError('SQL passed to comment parser did not start with a comment')

        if not self.sql.count('*/'):
            self._parsing_errors.append('Could not find closing comment indicator, */')
            return self.sql

        # otherwise this is very straight-forward
        index = self.sql.index('*/')
        self.comment = self.sql[2:index].strip()
        self._values = {'commment': self.comment}
        self.matched = True
        return self.sql[index + 2:].strip()
