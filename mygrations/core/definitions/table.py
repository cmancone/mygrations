from __future__ import annotations
from typing import Any, Dict, List, Set, Union
from collections import OrderedDict
from .rows import Rows
from .option import Option
from .columns.column import Column
from .index import Index
from .constraint import Constraint
from ..operations.create_table import CreateTable
class Table:
    _columns: Dict[str, Column] = None
    _constraints: Dict[str, Constraint] = None
    _indexes: Dict[str, Constraint] = None
    _indexed_columns = None
    _name: str = ''
    _options: List[Option] = None
    _primary: Index = None
    _rows: Dict[int, List[Union[str, int]]] = None
    _tracking_rows: bool = False
    _schema_errors: List[str] = None
    _schema_warnings: List[str] = None
    _global_errors: List[str] = None
    _global_warnings: List[str] = None

    def __init__(
        self,
        name: str = '',
        columns: List[Column] = None,
        indexes: List[Index] = None,
        constraints: List[Constraint] = None,
        options: List[Option] = None
    ):
        self._name = name
        self._options = [*options] if options else []
        self._primary = None
        self._constraints = {}
        self._columns = {}
        self._indexes = {}
        self._parsing_errors = None
        self._parsing_warnings = None
        self._schema_errors = None
        self._schema_warnings = None
        self._global_errors = []
        self._global_warnings = []
        self._final_global_errors = None
        self._final_global_warnings = None
        self._raw_columns = columns if columns is not None else []
        self._raw_constraints = constraints if constraints is not None else []
        self._raw_indexes = indexes if indexes is not None else []

        if columns is not None:
            for column in columns:
                self.add_column(column)
        if constraints is not None:
            for constraint in constraints:
                self.add_constraint(constraint)
        if indexes is not None:
            for index in indexes:
                self.add_index(index)

    # Errors are no longer tracked live. Instead, I need to finish adjusting the flow so that if any
    # of the error fetchers are called, then the errors are collected from all children and then the
    # proper errors are returned.

    @property
    def global_errors(self):
        """ Public getter.  Returns a list of schema errors

        :returns: A list of schema errors
        :rtype: list
        """
        if self._schema_errors is None:
            self._find_all_errors()
        return self._final_global_errors

    @property
    def global_warnings(self):
        """ Public getter.  Returns a list of schema warnings

        :returns: A list of schema warnings
        :rtype: list
        """
        if self._schema_errors is None:
            self._find_all_errors()
        return self._final_global_warnings

    @property
    def schema_errors(self):
        """ Public getter.  Returns a list of schema errors

        :returns: A list of schema errors
        :rtype: list
        """
        if self._schema_errors is None:
            self._find_all_errors()
        return self._schema_errors

    @property
    def schema_warnings(self):
        """ Public getter.  Returns a list of schema warnings

        :returns: A list of schema warnings
        :rtype: list
        """
        if self._schema_errors is None:
            self._find_all_errors()
        return self._schema_warnings

    @property
    def parsing_errors(self):
        """ Public getter.  Returns a list of schema errors

        :returns: A list of schema errors
        :rtype: list
        """
        if self._schema_errors is None:
            self._find_all_errors()
        return self._parsing_errors

    @property
    def parsing_warnings(self):
        """ Public getter.  Returns a list of schema warnings

        :returns: A list of schema warnings
        :rtype: list
        """
        if self._schema_errors is None:
            self._find_all_errors()
        return self._parsing_warnings

    @property
    def name(self):
        """ Public getter.  Returns the name of the table.

        :returns: The table name
        :rtype: string
        """

        return self._name

    @property
    def options(self):
        """ Public getter.  Returns a list of table options

        :returns: Table options
        :rtype: list
        """

        return self._options

    def _find_all_errors(self):
        self._schema_errors = []
        self._schema_warnings = []
        self._parsing_errors = []
        self._parsing_warnings = []
        if self._global_errors is not None:
            self._final_global_errors = [*self._global_errors]
        if self._global_warnings is not None:
            self._final_global_warnings = [*self._global_warnings]

        if not self.name:
            self._schema_errors.append("Table missing name")
        if not len(self.columns):
            self._schema_errors.append(f"Table '{self.name}' does not have any columns")

        # start with errors from "children" and append the table name for context
        for type_to_check in [self._columns, self._indexes, self._constraints]:
            for to_check in type_to_check.values():
                for error in to_check.schema_errors:
                    self._schema_errors.append(f"{error} in table '{self.name}'")
                for warning in to_check.schema_warnings:
                    self._schema_warnings.append(f"{warning} in table '{self.name}'")
                for error in to_check.parsing_errors:
                    self._parsing_errors.append(f"{error} in table '{self.name}'")
                for warning in to_check.parsing_warnings:
                    self._parsing_warnings.append(f"{error} in table '{self.name}'")
                if hasattr(to_check, 'global_errors'):
                    for warning in to_check.global_errors:
                        self._final_global_errors.append(f"{error} in table '{self.name}'")
                if hasattr(to_check, 'global_warnings'):
                    for warning in to_check.global_warnings:
                        self._final_global_warnings.append(f"{error} in table '{self.name}'")

        # duplicate names.  This shouldn't really be possible anymore because the add_ methods will
        # throw an exception if we try to add a duplicate, but I'll leave this in just in case.
        for (name, to_check) in {
            'columns': self._columns,
            'constraints': self._constraints,
            'indexes': self._indexes
        }.items():
            if len(to_check) == len(getattr(self, name)):
                continue
            label = name.rstrip('es').rstrip('s')
            found = {}
            duplicates = {}
            for item in to_check:
                if item.name in found:
                    duplicates[item.name] = True
                    continue
                found[item.name] = True
            for key in duplicates.keys():
                self._schema_errors.append(f"Duplicate {label} name found in table '{self.name}': '{key}'")

        # more than one primary key
        primaries = list(filter(lambda index: index.is_primary(), self._indexes.values()))
        if len(primaries) > 1:
            self._schema_errors.append(f"Table '{self.name}' has more than one PRIMARY index")

        # auto increment checks
        if self._columns:
            auto_increment = list(filter(lambda column: column.auto_increment, self._columns.values()))
            if len(auto_increment):
                if len(auto_increment) > 1:
                    self._schema_errors.append(f"Table '{self.name}' has more than one AUTO_INCREMENT column")
                elif not primaries:
                    self._schema_errors.append(
                        f"Table '{self.name}' has an AUTO_INCREMENT column but is missing the PRIMARY index"
                    )
                elif primaries[0].columns[0] != auto_increment[0].name:
                    self.schema_errors.append(
                        "Mismatched indexes in table '%s': column '%s' is the AUTO_INCREMENT column but '%s' is the PRIMARY index column"
                        % (self.name, auto_increment[0].name, primaries[0].columns[0])
                    )

        # indexes on non-existent columns
        for index in self._indexes.values():
            for column in index.columns:
                if not column in self.columns:
                    self._schema_errors.append(
                        f"Table '{self.name}' has index '{index.name}' that references non-existent column '{column}'"
                    )

        # we don't bother checking the constraints to see if they are valid because these are
        # best checked at the database level (since, by definition, foreign key constraints are *typically*
        # against other tables, not within a single table.

    def mark_tracking_rows(self):
        """ Marks the table as having had its rows read, for bookeeping purposes

        The reason this is here is because we keep track of whether or not we are "tracking" rows
        for the current table.  This is for bookeeping purposes, largely as a safe-guard attempt
        to try to identify any more subtle bugs that might creep in.  Normally self._tracking_rows
        gets set to True when we add rows to a table, but if a table is empty then rows will never
        get added, and instead this method must be called to mark the rows as "tracked".
        """
        self._tracking_rows = True
        if self._rows is None:
            self._rows = OrderedDict()

    @property
    def tracking_rows(self) -> bool:
        """ Public getter.  Returns True/False to denote whether or not this table is tracking row records

        To be clear on the distinction: just about any table might have rows.  However,
        that doesn't mean that the mygration system should be syncing rows for that table.
        self.tracking_rows == True denotes that the mygration system thinks that we
        should probably be syncing rows for this table.

        :returns: Whether or not the mygration system is tracking rows on the table
        """
        return self._tracking_rows

    @property
    def columns(self) -> Dict[str, Column]:
        """ Public getter.  Returns an ordered dictionary of table columns """
        return self._columns

    @property
    def indexes(self) -> Dict[str, Index]:
        """ Public getter.  Returns an ordered dictionary of table indexes """
        return self._indexes

    @property
    def constraints(self) -> Dict[str, Constraint]:
        """ Public getter.  Returns an ordered dictionary of table constraints """
        return self._constraints

    @property
    def primary(self) -> Index:
        """ Public getter.  Returns the index object for the primary key """
        return self._primary

    @property
    def rows(self) -> Dict[int, List[Union[str, int]]]:
        """ Public getter.  Returns an ordered dictionary with row data by id """
        return None if self._rows is None else self._rows

    def add_rows(self, rows: Rows) -> Union[str, bool]:
        """ Adds rows to the table

        The rows object has some flexibility in terms of columns: it doesn't just
        assume that a value is provided for every column in the table.  Rather,
        there can be a list of columns and only those columns have values (which
        supports the equivalent of MySQL INSERT queries which only specify values
        for some columns).

        Rows with errors will not be processed

        :returns: An error string if an error is encountered, otherwise True/False
        """
        self._schema_errors = None
        self._schema_warnings = None
        if not isinstance(rows, Rows):
            raise ValueError(
                f"Only objects of class mygrations.core.definitions.rows can be added as rows to a table.  Instead I received an object of class '{rows.__class__.__name__}'"
            )

        if rows.parsing_errors:
            self._global_errors.extend(rows.parsing_errors)
        if rows.parsing_warnings:
            self._global_warnings.extend(rows.parsing_warnings)

        self._tracking_rows = True
        if self._rows is None:
            self._rows = OrderedDict()

        # the rows object may have a list of columns.  If not use our own list of columns
        # remember that self._columns is an OrderedDict so converting its keys to a list
        # actually preserves the order (which is a requirement for us)
        columns = rows.columns if rows.num_explicit_columns else list(self._columns.keys())
        if 'id' not in columns:
            self._global_errors.append(
                "A column named 'id' is required to manage rows in the table, but the id column is missing in the rows for table %s"
                % (self._name, )
            )
            return
        id_index = columns.index('id')

        for values in rows.raw_rows:
            # rows without explicit columns must be checked for matching columns
            if not rows.num_explicit_columns and len(values) != len(columns):
                self._global_errors.append(
                    'Insert values has wrong number of values for table %s and row %s' % (self._name, values)
                )
                continue

            # we need to know the id of this record
            row_id = str(values[id_index])
            if not row_id:
                self._global_errors.append(
                    'Row is missing a value for the id column for table %s and row %s' % (self._name, values)
                )
                continue

            if row_id in self._rows:
                self._global_errors.append('Duplicate row id found for table %s and row %s' % (self.name, values))
                continue

            if not row_id:
                self._global_errors.append('Invalid row id of %s found for table %s' % (row_id, self.name))
                continue

            self._rows[row_id] = OrderedDict(zip(columns, values))
            self._rows[row_id]['id'] = row_id

        return True

    def add_raw_row(self, row: Dict[str, Union[str, int]]) -> Union[str, bool]:
        """ Adds a row into the table as a dictionary instead of a row object

        A bit of repetition here.  This is similar to what happens inside the main
        loop of self.add_rows, but different enough that I'm not trying to combine
        them right this second.

        :returns: An error string if an error is encountered, otherwise True/False
        """
        self._schema_errors = None
        self._schema_warnings = None
        self._tracking_rows = True
        if self._rows is None:
            self._rows = OrderedDict()

        row_id = str(row.get('id'))
        if not row_id:
            raise ValueError("Cannot manage records without an 'id' column and value")
        if row_id in self._rows:
            return 'Duplicate row id found for table %s and row %s' % (self._name, row)

        # make sure we have a value for every column in the row, and build an OrderedDict
        converted_row = OrderedDict()
        for column in self._columns.keys():
            if column in row:
                converted_row[column] = row[column]
            else:
                converted_row[column] = self._columns[column].default
        converted_row['id'] = row_id

        self._rows[row_id] = converted_row

    def column_before(self, column_name: str) -> Union[str, bool]:
        """ Returns the name of the column that comes before a given row.

        Returns true if the column is at the beginning of the table

        :returns: The name of the column before the given column, or True if at the beginning
        """
        # this works because we used an OrderedDict
        columns = [col for col in self.columns.keys()]

        if not column_name in columns:
            raise ValueError(
                "Cannot return column before %s because %s does not exist in table %s" %
                (column_name, column_name, self.name)
            )

        index = columns.index(column_name)
        if index == 0:
            return True

        return columns[index - 1]

    def column_is_indexed(self, column: Union[str, Column]) -> bool:
        """ Returns True/False to denote whether or not the column has a useable index """
        if type(column) != str:
            column = column.name
        if column not in self._columns:
            return False

        # best way to do this is with a set.  We'll keep a record of all indexed columns
        # the column is indexed if an index has that column in the first position
        if self._indexed_columns is None:
            self._indexed_columns = set([index.columns[0] for index in self._indexes.values()])
        return column in self._indexed_columns

    def __str__(self) -> str:
        return str(self.create())

    def create(self, nice=False):
        """ Returns a create table operation that can create this table

        :param nice: Whether or not to return a nicely formatted CREATE TABLE command
        :returns: A create table operation
        """
        return CreateTable(self, nice)

    def nice(self) -> str:
        return str(self.create(True))

    def add_column(self, column: Column, position=False):
        """ Adds a column to the table

        The value of position matches self.position from mygrations.formats.mysql.mygration.operations.add_column

        :param column: The column to add
        :param position: Where to put the column
        """
        self._schema_errors = None
        self._schema_warnings = None
        if column.name in self._columns:
            raise ValueError("Cannot add column %s because %s already exists" % (column.name, column.name))

        # putting it at the end is easy
        if not position:
            self._columns[column.name] = column
            return None

        # beginning is also easy
        if position == True:
            self._columns[column.name] = column
            self._columns.move_to_end(column.name, last=False)
            return None

        # now it is tricky
        found = False
        new_columns = OrderedDict()
        for key, value in self._columns.items():
            new_columns[key] = value
            if key == position:
                new_columns[column.name] = column
                found = True

        if not found:
            raise ValueError(
                "Cannot add column %s after %s because %s does not exist" % (column.name, position, position)
            )

        self._columns = new_columns
        return None

    def remove_column(self, column: Union[str, Column]):
        """ Removes a column from the table """
        self._schema_errors = None
        self._schema_warnings = None
        column_name = column if type(column) == str else column.name
        if not column_name in self._columns:
            raise ValueError("Cannot remove column %s because column %s does not exist" % (column_name, column_name))
        self._columns.pop(column_name, None)

    def change_column(self, new_column: Column):
        """ Changes a column.  This does not currently support renaming columns """
        self._schema_errors = None
        self._schema_warnings = None
        if not new_column.name in self._columns:
            raise ValueError(
                "Cannot modify column %s because column %s does not exist" % (new_column.name, new_column.name)
            )
        self._columns[new_column.name] = new_column

    def add_index(self, index: Index):
        """ Adds an index to the table """
        self._schema_errors = None
        self._schema_warnings = None
        if index.name in self._indexes:
            raise ValueError("Cannot add index %s because index %s already exists" % (index.name, index.name))
        if index.index_type == 'PRIMARY':
            self._primary = index
        self._indexes[index.name] = index

        if self._indexed_columns is not None:
            self._indexed_columns.add(index.columns[0])

    def remove_index(self, index: Union[str, Index]):
        """ Removes an index from the table """
        self._schema_errors = None
        self._schema_warnings = None
        index_name = index if type(index) == str else index.name
        if index_name not in self._indexes:
            raise ValueError("Cannot remove index %s because index %s does not exist" % (index_name, index_name))

        indexed_column = self._indexes[index_name].columns[0]
        self._indexes.pop(index_name, None)
        if self._indexed_columns is not None:
            self._indexed_columns.discard(indexed_column)

    def change_index(self, new_index: Index):
        """ Changes an index.  This does not currently support renaming """
        self._schema_errors = None
        self._schema_warnings = None
        if not new_index.name in self._indexes:
            raise ValueError(
                "Cannot modify index %s because index %s does not exist" % (new_index.name, new_index.name)
            )

        if self._indexed_columns is not None:
            self._indexed_columns.discard(self._indexes[new_index.name].columns[0])
        self._indexes[new_index.name] = new_index

        if self._indexed_columns is not None:
            self._indexed_columns.add(new_index.columns[0])

    def add_constraint(self, constraint: Constraint):
        """ Adds a constraint to the table """
        self._schema_errors = None
        self._schema_warnings = None
        if constraint.name in self._constraints:
            raise ValueError(
                "Cannot add constraint %s because constraint %s already exists" % (constraint.name, constraint.name)
            )
        self._constraints[constraint.name] = constraint

    def remove_constraint(self, constraint: Union[str, Constraint]):
        """ Removes an constraint from the table """
        self._schema_errors = None
        self._schema_warnings = None
        if type(constraint) != str:
            constraint = constraint.name
        if constraint not in self._constraints:
            raise ValueError(
                "Cannot remove constraint %s because constraint %s does not exist" % (constraint, constraint)
            )
        self._constraints.pop(constraint, None)

    def change_constraint(self, new_constraint):
        """ Changes a constraint. This does not currently support renaming. """
        self._schema_errors = None
        self._schema_warnings = None
        if not new_constraint.name in self._constraints:
            raise ValueError(
                "Cannot modify constraint %s because constraint %s does not exist" %
                (new_constraint.name, new_constraint.name)
            )
        self._constraints[new_constraint.name] = new_constraint

    def _loose_equal(self, val1: Union[str, int], val2: Union[str, int]) -> bool:
        """ Performs a looser comparison, as values might have different types depending on whether they came out of a database or file

        Returns true if the two values are equal, even if one is a string and the other an int.
        """
        # if we don't have a type mistmatch then this is easy
        if type(val1) == type(val2):
            return val1 == val2

        # otherwise see if we can cheat and just convert to strings
        return str(val1) == str(val2)

    def to(self, comparison_table, split_operations=False):
        """ Compares two tables to eachother and returns a list of operations which can bring the structure of the second in line with the first

        In other words, this pseudo code will make table have the same structure as comparison_table

        for operation in table.to( comparison_table ):
            table.apply( operation )

        if split_operations is True then a dict of migration operations will be returned to separate
        foreign key operations from everything else.  The dict will have up to three keys: [ 'removed_fks', 'fks', 'kitchen_sink' ]

        'fks' contains the alter statement operation needed to add/change/remove foreign keys
        'kitchen_sink' contains everything else

        If that division of labor seems arbitrary, it isn't: it is separated out that
        way due to the needs of the overall algorithm.

        If split_operations is false then a single alter table operation will be returned that encompasses all changes

        :param comparison_table: A table to find differences with
        :param split_operations: Whether to combine all operations in one alter table or separate them
        :type comparison_table: mygrations.formats.mysql.definitions.table
        :type split_operations: bool
        :returns: A list of operations to apply to table
        :rtype: list[mygrations.formats.mysql.mygrations.operations.*] | dict
        """
        raise NotImplementedError()

    def to_rows(self, from_table=None):
        """ Compares two tables to eachother and returns a list of operations which can bring the rows of this table in line with the other

        It's important to note (and probably important to think through and change eventually)
        that this method has the opposite meaning of `mygrations.formats.mysql.definitions.table.to()`
        That method is called on the `from` table and operations on the (required) `to` table.
        This method is called on the `to` table and can (optionally) be passed in a `from` table.

        :param from_table: A table to find differences with (or None)
        :type from_table: mygrations.formats.mysql.definitions.table
        :returns: A list of operations to apply to table
        :rtype: list[mygrations.formats.mysql.mygrations.operations.*]
        """
        raise NotImplementedError()

    def _differences(self, from_list: Dict[str, Any], to_list: Dict[str, Any]):
        """
        Calculates the difference between two OrderedDicts.

        https://codereview.stackexchange.com/a/176303/140581

        :param from_list: OrderedDict
        :param to_list: OrderedDict
        :return: (added, removed, overlap)
        """

        return ([key for key in to_list if key not in from_list], [key for key in from_list if key not in to_list],
                [key for key in from_list if key in to_list])

    def apply_operation(self, operation):
        """
        Applies an operation to the table

        :param operation: The operation to apply
        :type operation: mygrations.formats.mysql.mygration.operations.*
        """
        operation.apply_to_table(self)
