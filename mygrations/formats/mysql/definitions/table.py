from collections import OrderedDict
from .rows import rows as rows_definition

from ..mygrations.operations.alter_table import alter_table
from ..mygrations.operations.add_column import add_column
from ..mygrations.operations.change_column import change_column
from ..mygrations.operations.remove_column import remove_column
from ..mygrations.operations.add_key import add_key
from ..mygrations.operations.change_key import change_key
from ..mygrations.operations.remove_key import remove_key
from ..mygrations.operations.add_constraint import add_constraint
from ..mygrations.operations.change_constraint import change_constraint
from ..mygrations.operations.remove_constraint import remove_constraint

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

    @property
    def auto_increment( self ):
        """ Public getter.  Returns the autoincrement for the table

        :returns: The auto increment
        :rtype: int
        """
        return self._auto_increment

    @property
    def rows( self ):
        """ Public getter.  Returns an ordered dictionary with row data by id

        :returns: An ordered dictionary with row data by id
        :rtype: OrderedDict
        """
        return [] if self._rows is None else self._rows

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
                row_id = int( values[id_index] )
            except ValuerError:
                row_id = self._auto_increment

            self._auto_increment = max( self._auto_increment, row_id + 1 )
            if row_id in self._rows:
                return 'Duplicate row id found for table %s and row %s' % ( self._name, values )

            self._rows[row_id] = OrderedDict( zip( columns, values ) )

        return True

    def column_before( self, column_name ):
        """ Returns the name of the column that comes before a given row.

        Returns true if the column is at the beginning of the table

        :param column_name: The name of the column to find the position for
        :type column_name: str
        :returns: The name of the column before the given column, or True if at the beginning
        :rtype: string|True
        """
        # this works because we used an OrderedDict
        columns = [ col for col in self.columns.keys() ]

        if not column_name in columns:
            raise ValueError( "Cannot return column before %s because %s does not exist in table %s" % (column_name, column_name, self.name) )

        index = columns.index( column_name )
        if index == 0:
            return True

        return columns[index-1]

    def to( self, comparison_table, split_operations = True ):
        """ Compares two tables to eachother and returns a list of operations which can bring the structure of the second in line with the first

        In other words, this pseudo code will make table have the same structure as comparison_table

        for operation in (comparison_table - table):
            table.apply( operation )

        :param comparison_table: A table to find differences with
        :type comparison_table: mygrations.formats.mysql.definitions.table
        :returns: A list of operations to apply to table
        :rtype: list[mygrations.formats.mysql.mygrations.operations.*]
        """
        # start with the columns, obviously
        operations = []

        ( added_columns, removed_columns, overlap_columns ) = self.differences( self.columns, comparison_table.columns )
        ( added_keys, removed_keys, overlap_keys ) = self.differences( self.indexes, comparison_table.indexes )
        ( added_constraints, removed_constraints, overlap_constraints ) = self.differences( self.constraints, comparison_table.constraints )

        # keeping in mind the overall algorithm, we're going to separate out all changes into three alter statments
        # these are broken up according to the way that the system has to process them to make sure that foreign
        # keys are not violated during the process
        # 1. Adding columns, changing columns, adding keys, changing keys, removing keys, removing foreign keys
        # 2. Adding foreign keys, changing foreign keys
        # 3. Removing columns
        primary_alter = alter_table( self.name )
        for new_column in added_columns:
            primary_alter.add_operation( add_column( comparison_table.columns[new_column], comparison_table.column_before( new_column ) ) )

        for overlap_column in overlap_columns:
            # it's really easy to tell if a column changed
            if str( self.columns[overlap_column] ) == str( comparison_table.columns[overlap_column] ):
                continue
            primary_alter.add_operation( change_column( comparison_table.columns[overlap_column] ) )

        # indexes also go in that first alter table
        for new_key in added_keys:
            primary_alter.add_operation( add_key( comparison_table.indexes[new_key] ) )
        for removed_key in removed_keys:
            primary_alter.add_operation( remove_key( self.indexes[removed_key] ) )
        for overlap_key in overlap_keys:
            if str( self.indexes[overlap_key] ) == str( comparison_table.indexes[overlap_key] ):
                continue
            primary_alter.add_operation( change_key( comparison_table.indexes[overlap_key] ) )

        # removed FKs can also go in the first alter table
        for removed_constraint in removed_constraints:
            primary_alter.add_operation( remove_constraint( self.constraints[removed_constraint] ) )

        # adding and changing foreign keys gets their own alter
        constraints = alter_table( self.name )
        for added_constraint in added_constraints:
            constraints.add_operation( add_constraint( comparison_table.constraints[added_constraint] ) )
        for overlap_constraint in overlap_constraints:
            if str( self.constraints[overlap_constraint] ) == str( comparison_table.constraints[overlap_constraint] ):
                continue
            constraints.add_operation( change_constraint( comparison_table.constraints[overlap_constraint] ) )

        # removed columns get their own alter
        remove_columns_alter = alter_table( self.name )
        for removed_column in removed_columns:
            remove_columns_alter.add_operation( remove_column( self.columns[removed_column] ) )

        # now put it all together
        if split_operations:
            if primary_alter:
                operations.append( primary_alter )
            if constraints:
                operations.append( constraints )
            if remove_columns_alter:
                operations.append( remove_columns_alter )
        else:
            for operation in constraints:
                primary_alter.add_operation( operation )
            for operation in remove_columns_alter:
                primary_alter.add_operation( operation )
            if primary_alter:
                operations.append( primary_alter )

        return operations

    def differences(self, a, b):
        """
        Calculates the difference between two OrderedDicts.

        https://codereview.stackexchange.com/a/176303/140581

        :param a: OrderedDict
        :param b: OrderedDict
        :return: (added, removed, overlap)
        """

        return (
            [key for key in b if key not in a],
            [key for key in a if key not in b],
            [key for key in a if key in b]
        )
