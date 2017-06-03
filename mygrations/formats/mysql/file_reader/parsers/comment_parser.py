class comment_parser( object ):

    sql = ''

    def __init__( self, sql ):
        """ parser = comment_parser( sql )

        Processes any comments at the start of the string

        :param sql: The SQL string to parse
        :type sql: string
        """

        self.sql = sql.strip();
        self.comment = ''

    def parse( self ):
        """ res = paser.parse()

        Parses the SQL, storing the comment and returning an SQL string with the comment removed

        :returns: The SQL string with the first comment removed
        :rtype: string

        :Example:
                >>> import comment_parser
                >>> parser = comment_parser( '--Some SQL\nINSERT INTO some_table (1,2)' )
                >>> without_comment = parser.parse()
                >>> print parser.comment
                Some SQL
                >>> print( without_comment )
                INSERT INTO some_table (1,2)
        """

        # what kind of comment are we dealing with?
        # -- and # go to the end of the line.  /* goes to */
        if self.sql[0] == '#' or self.sql[:2] == '--':

            # which is really easy if there is no newline: the
            # whole thing is our comment and there is no data left
            if not self.sql.count( '\n' ):
                self.comment = self.sql
                return '';

            # otherwise just find the newline and return the rest
            else:
                index = self.sql.index( '\n' )
                self.comment = self.sql[:index]
                return self.sql[index+1:].strip()

        # then we should be dealing with /* ... */.  Our line should
        # start with it or we have a problem
        if self.sql[:1] != '/*':
            raise ValueError( 'SQL passed to comment parser did not start with a comment' )

        if not self.sql.count( '*/' ):
            raise SyntaxError( 'Could not find closing comment indicator, */' )

        # otherwise this is very straight-forward
        index = self.sql.index( '*/' )
        self.comment = self.sql[2:index].strip()
        return self.sql[index+2:].strip()
