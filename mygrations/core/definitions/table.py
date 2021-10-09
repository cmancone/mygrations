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
    _auto_increment: int = 1
    _columns: Dict[str, Column] = None
    _constraints: Dict[str, Constraint] = None
    _errors: List[str] = None
    _name: str = ''
    _options: List[Option] = None
    _primary: Index = None
    _rows: Dict[int, List[Union[str, int]]] = None
    _tracking_rows: bool = False
    _warnings: List[str] = None

    def __init__(
        self, name: str, columns: List[Column], indexes: List[Index], constraints: List[Constraint],
        options: List[Option]
    ):
        self._columns = OrderedDict()
        self._constraints = OrderedDict()
        self._errors = []
        self._indexes = OrderedDict()
        self._name = name
        self._options = options
        self._primary = None
        self._raw_columns = columns
        self._raw_constraints = constraints
        self._raw_indexes = indexes
        self._warnings = []

        self._columns = OrderedDict((col.name, col) for col in columns)
        self._constraints = OrderedDict((constraint.name, constraint) for constraint in constraints)
        self._indexes = OrderedDict((index.name, index) for index in indexes)

        # It is somewhat non-sensical that we check for errors and warnings in the constructor, but allow
        # columns/constraints/indexes to be allowed later as well.  It ended up like this simply because that's
        # how the other classes are organized, but the other classes don't allow changes to be made after
        # instatiation.  Therefore this will likely cause problems in the future, but I'm being lazy right now.
        self._check_for_errors_and_warnings(columns, constraints, indexes)

        for index in self._indexes.values():
            if index.index_type == 'PRIMARY':
                self._primary = index
                break

    def _check_for_errors_and_warnings(
        self, columns: List[Column], constraints: List[Constraint], indexes: List[Index]
    ):
        """ Check for errors and warnings for the initial data

        The raw list of columns/constraints/indexes must be passed in because the constructor
        converts these to ordered dicts, which means duplicate names will result in missing entries.
        We want to check for duplicate entries, so therefore we need the original list.
        """
        self._errors = []
        self._warnings = []

        if not self.name:
            self._errors.append("Table missing name")
        if not len(self.columns):
            self._errors.append(f"Table '{self.name}' does not have any columns")
            # if we have no columns then none of these other checks apply
            return None

        # start with errors from "children" and append the table name for context
        for type_to_check in [columns, indexes, constraints]:
            for to_check in type_to_check:
                for error in to_check.errors:
                    self._errors.append(f"{error} in table '{self.name}'")
                for warning in to_check.warnings:
                    self._warnings.append(f"{warning} in table '{self.name}'")

        # duplicate names
        for (name, to_check) in {'columns': columns, 'constraints': constraints, 'indexes': indexes}.items():
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
                self._errors.append(f"Duplicate {label} name found in table '{self.name}': '{key}'")

        # more than one primary key
        primaries = list(filter(lambda index: index.is_primary(), indexes))
        if len(primaries) > 1:
            self._errors.append(f"Table '{self.name}' has more than one PRIMARY index")

        # auto increment checks
        auto_increment = list(filter(lambda column: column.auto_increment, columns))
        if len(auto_increment) > 1:
            self._errors.append(f"Table '{self.name}' has more than one AUTO_INCREMENT column")
        elif not primaries:
            self._errors.append(f"Table '{self.name}' has an AUTO_INCREMENT column but is missing the PRIMARY index")
        elif primaries[0].columns[0] != auto_increment[0].name:
            self._errors.append(
                "Mismatched indexes in table '%s': column '%s' is the AUTO_INCREMENT column but '%s' is the PRIMARY index column"
                % (self.name, auto_increment[0].name, primaries[0].columns[0])
            )

        # indexes on non-existent columns
        for index in self.indexes.values():
            for column in index.columns:
                if not column in self.columns:
                    self._errors.append(
                        f"Table '{self.name}' has index '{index.name}' that references non-existent column '{column}'"
                    )

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
    def errors(self) -> List[str]:
        """ Public getter.  Returns a list of parsing errors """
        return [] if self._errors is None else self._errors

    @property
    def warnings(self) -> List[str]:
        """ Public getter.  Returns a list of parsing/table warnings """
        return [] if self._warnings is None else self._warnings

    @property
    def auto_increment(self) -> int:
        """ Public getter.  Returns the autoincrement value for the table """
        return self._auto_increment

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
        if not isinstance(rows, rows_definition):
            raise ValueError(
                'Only objects of class mygrations.formats.mysql.definitions.rows can be added as rows to a table'
            )

        # we can't process guys with errors
        if rows._errors:
            return False

        self._tracking_rows = True
        if self._rows is None:
            self._rows = OrderedDict()

        # the rows object may have a list of columns.  If not use our own list of columns
        # remember that self._columns is an OrderedDict so converting its keys to a list
        # actually preserves the order (which is a requirement for us)
        columns = rows.columns if rows.num_explicit_columns else list(self._columns.keys())

        for values in rows.raw_rows:
            # rows without explicit columns must be checked for matching columns
            if not rows.num_explicit_columns and len(values) != len(columns):
                return 'Insert values has wrong number of values for table %s and row %s' % (self._name, values)

            # we need to know the id of this record, which means we need
            # to know where in the list of values the id column lives
            try:
                id_index = columns.index('id')
                row_id = int(values[id_index])
            except ValueError:
                row_id = self._auto_increment

            self._auto_increment = max(self._auto_increment, row_id + 1)
            if row_id in self._rows:
                return 'Duplicate row id found for table %s and row %s' % (self.name, values)

            if not row_id:
                return 'Invalid row id of %s found for table %s' % (row_id, self.name)

            self._rows[row_id] = OrderedDict(zip(columns, values))

        return True

    def add_raw_row(self, row: Dict[str, Union[str, int]]) -> Union[str, bool]:
        """ Adds a row into the table as a dictionary instead of a row object

        A bit of repetition here.  This is similar to what happens inside the main
        loop of self.add_rows, but different enough that I'm not trying to combine
        them right this second.

        :returns: An error string if an error is encountered, otherwise True/False
        """
        self._tracking_rows = True
        if self._rows is None:
            self._rows = OrderedDict()

        row_id = row['id'] if 'id' in row else self._auto_increment
        self._auto_increment = max(self._auto_increment, row_id + 1)
        if row_id in self._rows:
            return 'Duplicate row id found for table %s and row %s' % (self._name, row)

        # make sure we have a value for every column in the row, and build an OrderedDict
        converted_row = OrderedDict()
        for column in self._columns.keys():
            if column in row:
                converted_row[column] = row[column]
            else:
                converted_row[column] = self._columns[column].default

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
        column_name = column if type(column) == str else column.name
        if not column_name in self._columns:
            raise ValueError("Cannot remove column %s because column %s does not exist" % (column_name, column_name))
        self._columns.pop(column_name, None)

    def change_column(self, new_column: Column):
        """ Changes a column.  This does not currently support renaming columns """
        if not new_column.name in self._columns:
            raise ValueError(
                "Cannot modify column %s because column %s does not exist" % (new_column.name, new_column.name)
            )
        self._columns[new_column.name] = new_column

    def add_index(self, index: Index):
        """ Adds an index to the table """
        if index.name in self._indexes:
            raise ValueError("Cannot add index %s because index %s already exists" % (index.name, index.name))
        self._indexes[index.name] = index

        if self._indexed_columns is not None:
            self._indexed_columns.add(index.columns[0])

    def remove_index(self, index: Union[str, Index]):
        """ Removes an index from the table """
        index_name = index if type(index) == str else index.name
        if index_name not in self._indexes:
            raise ValueError("Cannot remove index %s because index %s does not exist" % (index_name, index_name))

        indexed_column = self._indexes[index_name].columns[0]
        self._indexes.pop(index_name, None)
        if self._indexed_columns is not None:
            self._indexed_columns.discard(indexed_column)

    def change_index(self, new_index: Index):
        """ Changes an index.  This does not currently support renaming """
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
        if constraint.name in self._constraints:
            raise ValueError(
                "Cannot add constraint %s because constraint %s already exists" % (constraint.name, constraint.name)
            )
        self._constraints[constraint.name] = constraint

    def remove_constraint(self, constraint: Union[str, Constraint]):
        """ Removes an constraint from the table """
        if type(constraint) != str:
            constraint = constraint.name
        if constraint not in self._constraints:
            raise ValueError(
                "Cannot remove constraint %s because constraint %s does not exist" % (constraint, constraint)
            )
        self._constraints.pop(constraint, None)

    def change_constraint(self, new_constraint):
        """ Changes a constraint. This does not currently support renaming. """
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
        # start with the columns, obviously
        (added_columns, removed_columns, overlap_columns) = self._differences(self.columns, comparison_table.columns)
        (added_keys, removed_keys, overlap_keys) = self._differences(self.indexes, comparison_table.indexes)
        (added_constraints, removed_constraints,
         overlap_constraints) = self._differences(self.constraints, comparison_table.constraints)

        # keeping in mind the overall algorithm, we're going to separate out all changes into three alter statments
        # these are broken up according to the way that the system has to process them to make sure that foreign
        # keys are not violated during the process
        # 1. Adding columns, changing columns, adding keys, changing keys, removing keys, removing foreign keys
        # 2. Adding foreign keys, changing foreign keys
        # 3. Removing columns
        primary_alter = alter_table(self.name)
        for new_column in added_columns:
            primary_alter.add_operation(
                add_column(comparison_table.columns[new_column], comparison_table.column_before(new_column))
            )

        for overlap_column in overlap_columns:
            # it's really easy to tell if a column changed
            if str(self.columns[overlap_column]) == str(comparison_table.columns[overlap_column]):
                continue

            # FALSE POSITIVE CHECK:
            # if one column has collate/character set and the other doesn't, and that is the only difference,
            # then ignore this difference
            if self.columns[overlap_column].is_really_the_same_as(comparison_table.columns[overlap_column]):
                continue

            primary_alter.add_operation(change_column(comparison_table.columns[overlap_column]))

        for removed_column in removed_columns:
            primary_alter.add_operation(remove_column(self.columns[removed_column]))

        # indexes also go in that first alter table
        for new_key in added_keys:
            primary_alter.add_operation(add_key(comparison_table.indexes[new_key]))
        for removed_key in removed_keys:
            primary_alter.add_operation(remove_key(self.indexes[removed_key]))
        for overlap_key in overlap_keys:
            if str(self.indexes[overlap_key]) == str(comparison_table.indexes[overlap_key]):
                continue
            primary_alter.add_operation(change_key(comparison_table.indexes[overlap_key]))

        # removed foreign key constraints get their own alter because that should always happen first
        removed_constraints_alter = alter_table(self.name)
        for removed_constraint in removed_constraints:
            removed_constraints_alter.add_operation(remove_constraint(self.constraints[removed_constraint]))

        # adding/changing/removing foreign keys gets their own alter
        constraints = alter_table(self.name)
        for added_constraint in added_constraints:
            constraints.add_operation(add_constraint(comparison_table.constraints[added_constraint]))
        for overlap_constraint in overlap_constraints:
            if str(self.constraints[overlap_constraint]) == str(comparison_table.constraints[overlap_constraint]):
                continue

            # foreign key constraints are modified by first dropping the constraint and
            # then adding the new one.  However, these two operations cannot happen in the
            # same alter command.  Kinda a pain.  Oh well.
            removed_constraints_alter.add_operation(remove_constraint(self.constraints[overlap_constraint]))
            constraints.add_operation(add_constraint(comparison_table.constraints[overlap_constraint]))

        # now put it all together
        if split_operations:
            operations = {}
            if removed_constraints_alter:
                operations['removed_fks'] = removed_constraints_alter
            if primary_alter:
                operations['kitchen_sink'] = primary_alter
            if constraints:
                operations['fks'] = constraints
        else:
            operations = []
            for operation in constraints:
                primary_alter.add_operation(operation)
            if removed_constraints_alter:
                operations.append(removed_constraints_alter)
            if primary_alter:
                operations.append(primary_alter)

        return operations

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
        if from_table and not from_table.tracking_rows:
            raise ValueError(
                "Refusing to compare rows for table %s that is not tracking rows.  Technically I can, but this is probably a sign that you are doing something wrong"
                % (self.name)
            )

        (inserted_ids, deleted_ids, updated_ids) = self._differences(from_table.rows if from_table else {}, self.rows)

        operations = []
        for row_id in inserted_ids:
            operations.append(row_insert(self.name, self.rows[row_id]))

        for row_id in deleted_ids:
            operations.append(row_delete(self.name, row_id))

        for row_id in updated_ids:
            # try to be smart and not update if we don't have to
            (inserted_cols, deleted_cols, updated_cols) = self._differences(self.rows[row_id], from_table.rows[row_id])
            differences = False
            for col in updated_cols:
                if not self._loose_equal(self.rows[row_id][col], from_table.rows[row_id][col]):
                    differences = True
                    break

            if differences:
                operations.append(row_update(self.name, self.rows[row_id]))

        return operations

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
