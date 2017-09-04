from collections import OrderedDict
from .rows import rows as rows_definition

class table( object ):

    _name = ''
    _options = None
    _columns = None
    _indexes = None
    _constraints = None
    _primary = None
    _rows = None
    _errors = None
    _warnings = None
    _auto_increment = 1

    @property
    def name( self ):
        """ Public getter.  Returns the name of the column.

        :returns: The column name
        :rtype: string
        """

        return self._name

    @property
    def options( self ):
        """ Public getter.  Returns a list of table options

        :returns: Table options
        :rtype: list
        """

        return self._options

    @property
    def columns( self ):
        """ Public getter.  Returns an ordered dictionary of table columns

        :returns: Table columns
        :rtype: OrderedDict
        """

        return self._columns

    @property
    def indexes( self ):
        """ Public getter.  Returns an ordered dictionary of table indexes

        :returns: Table indexes
        :rtype: OrderedDict
        """

        return self._indexes

    @property
    def constraints( self ):
        """ Public getter.  Returns an ordered dictionary of table constraints

        :returns: Table constraints
        :rtype: OrderedDict
        """

        return self._constraints

    @property
    def primary( self ):
        """ Public getter.  Returns the index object for the primary key

        :returns: The index object of the primary key column
        :rtype: isinstance(formats.mysql.definitions.index)
        """

        return self._primary

    @property
    def errors( self ):
        """ Public getter.  Returns a list of parsing errors

        :returns: A list of parsing errors
        :rtype: list
        """
        return [] if self._errors is None else self._errors

    @property
    def warnings( self ):
        """ Public getter.  Returns a list of parsing/table warnings

        :returns: A list of parsing/table warnings
        :rtype: list
        """
        return [] if self._warnings is None else self._warnings

    def add_rows( self, rows ):
        """ Adds a mygrations.formats.mysql.definitions.rows object to the table

        The rows object has some flexibility in terms of columns: it doesn't just
        assume that a value is provided for every column in the table.  Rather,
        there can be a list of columns and only those columns have values (which
        supports the equivalent of MySQL INSERT queries which only specify values
        for some columns).

        Rows with errors will not be processed

        :param rows: The rows to process
        :type rows: mygrations.formats.mysql.definitions.rows
        :returns: An error string if an error is encountered, otherwise True/False
        :rtype: bool | string
        """
        if not isinstance( rows, rows_definition ):
            raise ValueError( 'Only objects of class mygrations.formats.mysql.definitions.rows can be added as rows to a table' )

        # we can't process guys with errors
        if rows._errors:
            return False

        if self._rows is None:
            self._rows = OrderedDict()

        # the rows object may have a list of columns.  If not use our own list of columns
        # remember that self._columns is an OrderedDict so converting its keys to a list
        # actually preserves the order (which is a requirement for us)
        columns = rows.columns if rows.num_explicit_columns else list(self._columns.keys())

        for values in rows.raw_rows:
            # rows without explicit columns must be checked for matching columns
            if not rows.num_explicit_columns and len( values ) != len( columns ):
                return 'Insert values has wrong number of values for table %s and row %s' % ( self._name, values )

            # we need to know the id of this record, which means we need
            # to know where in the list of values the id column lives
            try:
                id_index = columns.index( 'id' )
                row_id = values[id_index]
            except ValuerError:
                row_id = self._auto_increment

            self._auto_increment = max( self._auto_increment, row_id + 1 )
            if row_id in self._rows:
                return 'Duplicate row id found for table %s and row %s' % ( self._name, values )

            self._rows[row_id] = OrderedDict( zip( columns, values ) )
