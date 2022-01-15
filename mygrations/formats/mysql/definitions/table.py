from collections import OrderedDict
from .rows import Rows as RowsDefinition
from ..mygrations.operations.alter_table import AlterTable
from ..mygrations.operations.add_column import AddColumn
from ..mygrations.operations.change_column import ChangeColumn
from ..mygrations.operations.remove_column import RemoveColumn
from ..mygrations.operations.add_key import AddKey
from ..mygrations.operations.change_key import ChangeKey
from ..mygrations.operations.remove_key import RemoveKey
from ..mygrations.operations.add_constraint import AddConstraint
from ..mygrations.operations.change_constraint import ChangeConstraint
from ..mygrations.operations.remove_constraint import RemoveConstraint
from ..mygrations.operations.create_table import CreateTable
from ..mygrations.operations.row_delete import RowDelete
from ..mygrations.operations.row_insert import RowInsert
from ..mygrations.operations.row_update import RowUpdate
from mygrations.core.definitions.table import Table as BaseTable
class Table(BaseTable):
    def create(self, nice=False):
        """ Returns a create table operation that can create this table

        :param nice: Whether or not to return a nicely formatted CREATE TABLE command
        :type nice: bool
        :returns: A create table operation
        :rtype: mygrations.operations.CreateTable
        """
        return CreateTable(self, nice)

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
        primary_alter = AlterTable(self.name)
        for new_column in added_columns:
            primary_alter.add_operation(
                AddColumn(comparison_table.columns[new_column], comparison_table.column_before(new_column))
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

            primary_alter.add_operation(ChangeColumn(comparison_table.columns[overlap_column]))

        for removed_column in removed_columns:
            primary_alter.add_operation(RemoveColumn(self.columns[removed_column]))

        # indexes also go in that first alter table
        for new_key in added_keys:
            primary_alter.add_operation(AddKey(comparison_table.indexes[new_key]))
        for removed_key in removed_keys:
            primary_alter.add_operation(RemoveKey(self.indexes[removed_key]))
        for overlap_key in overlap_keys:
            if str(self.indexes[overlap_key]) == str(comparison_table.indexes[overlap_key]):
                continue
            primary_alter.add_operation(ChangeKey(comparison_table.indexes[overlap_key]))

        # removed foreign key constraints get their own alter because that should always happen first
        removed_constraints_alter = AlterTable(self.name)
        for removed_constraint in removed_constraints:
            removed_constraints_alter.add_operation(RemoveConstraint(self.constraints[removed_constraint]))

        # adding/changing/removing foreign keys gets their own alter
        constraints = AlterTable(self.name)
        for added_constraint in added_constraints:
            constraints.add_operation(AddConstraint(comparison_table.constraints[added_constraint]))
        for overlap_constraint in overlap_constraints:
            if str(self.constraints[overlap_constraint]) == str(comparison_table.constraints[overlap_constraint]):
                continue

            # foreign key constraints are modified by first dropping the constraint and
            # then adding the new one.  However, these two operations cannot happen in the
            # same alter command.  Kinda a pain.  Oh well.
            removed_constraints_alter.add_operation(RemoveConstraint(self.constraints[overlap_constraint]))
            constraints.add_operation(AddConstraint(comparison_table.constraints[overlap_constraint]))

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
            operations.append(RowInsert(self.name, self.rows[row_id]))

        for row_id in deleted_ids:
            operations.append(RowDelete(self.name, row_id))

        for row_id in updated_ids:
            # try to be smart and not update if we don't have to
            (inserted_cols, deleted_cols, updated_cols) = self._differences(self.rows[row_id], from_table.rows[row_id])
            differences = False
            for col in updated_cols:
                if not self._loose_equal(self.rows[row_id][col], from_table.rows[row_id][col]):
                    differences = True
                    break

            if differences:
                operations.append(RowUpdate(self.name, self.rows[row_id]))

        return operations
