from mygrations.formats.mysql.mygrations.operations.alter_table import AlterTable
from mygrations.formats.mysql.mygrations.operations.add_constraint import AddConstraint
from mygrations.formats.mysql.mygrations.operations.remove_constraint import RemoveConstraint
from mygrations.formats.mysql.mygrations.operations.remove_table import RemoveTable
from mygrations.formats.mysql.mygrations.operations.disable_checks import DisableChecks
from mygrations.formats.mysql.mygrations.operations.enable_checks import EnableChecks


class Mygration:
    """Creates a migration plan to update a database to a given spec.

    If only one database is passed in, it treats it as a structure to migrate
    to starting from a blank slate, which primariliy means just figuring out
    what order to add tables in to account for foreign key constraints.

    If two tables are present, then it will treat the second as the current
    database constraint, and will figure out steps to execute in action
    to update that second database to match the structure of the first.

    The general steps are:

    1. Check for foreign key errors: if the two database we are trying to migrate to doesn't support its own foreign key constraints, there is a show stopper
    2. Loop through tables to be added, "creating" them as their foreign key constraints are filled, and ignoring any that have interlocking dependencies
    3. Remove any FK constraints that are no longer used (done early to prevent trouble in the next step)
    4. Modify tables as needed.  If modifying tables involves adding foreign key constraints that are not fulfilled, ignore those and add them later
    5. See if we can add any remaining tables now that some table modifications have been applied
    6. If there are still any outstanding tables to add, remove any foreign key constraints that are not fulfilled and add the tables without them
    7. Apply all foreign key constraints that were previously ignored in steps 4 & 6
    8. Remove any tables that need to be removed
    """

    def __init__(self, db_to, db_from=None, disable_checks=True):
        """Create a migration plan

        :param db_to: The target database structure to migrate to
        :param db_from: The current database structure to migrate from
        :param disable_checks: Whether or not to add an operations to disable/re-enable FK checks
        :type db_to: mygrations.formats.mysql.definitions.database
        :type db_from: mygrations.formats.mysql.definitions.database
        :type disable_checks: True
        """

        self.db_to = db_to
        self.db_from = db_from
        self._disable_fk_checks = disable_checks

        # first things first: stop if we have any FK errors in the database
        # we are migrating to
        self._errors = []
        self._errors = self.db_to.errors

        if not self._errors:
            self._operations = self._process()
        else:
            self._operations = None

    @property
    def operations(self):
        """Public getter.  Returns list of operations to bring db_from to db_to

        If db_from doesn't exist then it will be a list of operations to
        create db_to.

        If there are 1215 errors that will prevent the migration, then
        operations will return None

        If the two databases are exactly the same then operations will
        be an empty list

        :returns: A list of table operations
        :rtype: None|[mygrations.formats.mysql.mygrations.operations.operation]
        """
        return self._operations

    @property
    def errors(self):
        """Public getter.  Returns list of 1215 errors (as strings)

        :returns: A list of 1215 error messages
        :rtype: [string]
        """
        return self._errors

    def __len__(self):
        return len(self._operations)

    def __bool__(self):
        return True if len(self._operations) else False

    def __str__(self):
        return "\n".join([str(x) for x in self._operations])

    def __iter__(self):
        return self._operations.__iter__()

    def _differences(self, from_dict, to_dict):
        """
        Calculates the difference between two OrderedDicts.

        https://codereview.stackexchange.com/a/176303/140581

        Duplication!!!! (formats.mysql.create_parser).  Sue me.

        :param a: OrderedDict
        :param b: OrderedDict
        :return: (added, removed, overlap)
        """

        return (
            [key for key in to_dict if key not in from_dict],
            [key for key in from_dict if key not in to_dict],
            [key for key in from_dict if key in to_dict],
        )

    def _process(self):
        """Figures out the operations needed to get to self.db_to

        Returns a list of operations that will migrate db_from to db_to

        For performance reasons the migrations are done with foreign key
        checks off: the first operation turns them off, and the last operation
        turns them on.

        MySQL does not allow ALTER TABLE to change the type of a column that
        participates in a foreign key constraint, even with SET FOREIGN_KEY_CHECKS=0.
        (MySQL error 3780).  To work around this, we detect column type changes on
        FK-involved columns and emit DROP FK / ALTER / ADD FK sequences.

        :return: Operations needed to complete the migration
        :rtype: [mygrations.formats.mysql.mygrations.operations]
        """
        operations = []
        if self._disable_fk_checks:
            operations.append(DisableChecks())

        # what tables have been added/changed/removed
        db_from_tables = self.db_from.tables if self.db_from else {}
        (tables_to_add, tables_to_remove, tables_to_update) = self._differences(db_from_tables, self.db_to.tables)

        for table_name in tables_to_add:
            operations.append(self.db_to.tables[table_name].create())

        fk_drop_ops, fk_add_ops, cycled_fks = self._find_fk_ops_for_column_type_changes(tables_to_update)

        operations.extend(fk_drop_ops)

        # Use split_operations=True to separate FK additions from column/key changes.
        # This ensures ALL column type changes across ALL tables complete before any
        # new FK constraints are added — preventing MySQL error 3780 when a child table
        # (e.g. company_domains) is processed before its parent (e.g. businesses)
        # alphabetically and tries to ADD FK before the parent column type is updated.
        deferred_fk_ops = []
        for table_name in tables_to_update:
            target_table = self.db_to.tables[table_name]
            source_table = self.db_from.tables[table_name]
            split_ops = source_table.to(target_table, True)

            if "removed_fks" in split_ops:
                filtered = self._strip_cycled_fk_ops(split_ops["removed_fks"], cycled_fks)
                if filtered:
                    operations.append(filtered)
            if "kitchen_sink" in split_ops:
                operations.append(split_ops["kitchen_sink"])
            if "fks" in split_ops:
                filtered = self._strip_cycled_fk_ops(split_ops["fks"], cycled_fks)
                if filtered:
                    deferred_fk_ops.append(filtered)

        operations.extend(deferred_fk_ops)
        operations.extend(fk_add_ops)

        for table_name in tables_to_remove:
            operations.append(RemoveTable(table_name))

        if self._disable_fk_checks:
            operations.append(EnableChecks())

        return operations

    def _find_fk_ops_for_column_type_changes(self, tables_to_update):
        """Finds FK constraints that must be temporarily dropped due to column type changes.

        MySQL error 3780 prevents ALTER TABLE from changing the type of a column involved
        in a foreign key constraint, even with FOREIGN_KEY_CHECKS=0.  This method detects
        such situations and returns the DROP/ADD operations needed to work around it.

        When the FK name in the live DB differs from the SQL files (e.g. MySQL auto-named
        'child_records_ibfk_1' vs file-generated 'business_id_businesses_fk'), we fall back
        to matching by column/reference (column_name, foreign_table_name, foreign_column_name).

        :param tables_to_update: List of table names being updated
        :returns: (drop_ops, add_ops, cycled_fk_names) where cycled_fk_names is a set of
            (table_name, constraint_name) tuples for deduplication with table.to().
            When source and target FK names differ, BOTH names are included in cycled_fk_names.
        :rtype: tuple(list, list, set)
        """
        if not self.db_from:
            return ([], [], set())

        changing_columns = {}
        for table_name in tables_to_update:
            source_table = self.db_from.tables[table_name]
            target_table = self.db_to.tables[table_name]

            for col_name in source_table.columns:
                if col_name not in target_table.columns:
                    continue
                source_col = source_table.columns[col_name]
                target_col = target_table.columns[col_name]
                if self._column_type_differs(source_col, target_col):
                    changing_columns[(table_name, col_name)] = True

        if not changing_columns:
            return ([], [], set())

        fks_to_cycle = {}

        for table_name, table in self.db_from.tables.items():
            if not table.constraints:
                continue
            for constraint_name, constraint in table.constraints.items():
                local_key = (table_name, constraint.column_name)
                foreign_key = (constraint.foreign_table_name, constraint.foreign_column_name)

                if local_key in changing_columns or foreign_key in changing_columns:
                    fk_key = (table_name, constraint_name)
                    if fk_key in fks_to_cycle:
                        continue

                    target_table = self.db_to.tables.get(table_name)
                    if not target_table:
                        # Table is being dropped — still need to DROP this FK before the
                        # column type change, but no ADD is needed (table will be removed).
                        fks_to_cycle[fk_key] = (constraint, None, None)
                        continue

                    target_constraint = None
                    target_constraint_name = None
                    if constraint_name in target_table.constraints:
                        target_constraint = target_table.constraints[constraint_name]
                        target_constraint_name = constraint_name
                    else:
                        # FK name mismatch (e.g. MySQL auto-named 'table_ibfk_1' vs
                        # file-generated 'col_table_fk').  Match by column/reference instead.
                        target_constraint = self._find_matching_constraint(target_table, constraint)
                        if target_constraint:
                            target_constraint_name = target_constraint.name

                    if not target_constraint:
                        continue

                    fks_to_cycle[fk_key] = (constraint, target_constraint, target_constraint_name)

        if not fks_to_cycle:
            return ([], [], set())

        drop_by_table = {}
        add_by_table = {}
        cycled_fk_names = set()
        # Track which target constraints have already been scheduled for ADD.
        # When the live DB has duplicate FKs (e.g. ibfk_1 through ibfk_18 all
        # referencing the same column/table), each maps to the SAME target
        # constraint via _find_matching_constraint().  We must DROP all source
        # duplicates but ADD the target constraint only once.
        added_targets = set()

        for (table_name, constraint_name), (
            source_constraint,
            target_constraint,
            target_constraint_name,
        ) in fks_to_cycle.items():
            drop_by_table.setdefault(table_name, []).append(RemoveConstraint(source_constraint))
            if target_constraint:
                add_key = (table_name, target_constraint_name)
                if add_key not in added_targets:
                    add_by_table.setdefault(table_name, []).append(AddConstraint(target_constraint))
                    added_targets.add(add_key)
            cycled_fk_names.add((table_name, constraint_name))
            if target_constraint_name and target_constraint_name != constraint_name:
                cycled_fk_names.add((table_name, target_constraint_name))

        drop_ops = []
        for table_name, ops in drop_by_table.items():
            alter = AlterTable(table_name)
            for op in ops:
                alter.add_operation(op)
            drop_ops.append(alter)

        add_ops = []
        for table_name, ops in add_by_table.items():
            alter = AlterTable(table_name)
            for op in ops:
                alter.add_operation(op)
            add_ops.append(alter)

        return (drop_ops, add_ops, cycled_fk_names)

    def _strip_cycled_fk_ops(self, alter, cycled_fks):
        """Removes FK operations from an AlterTable that are already handled by the cycle.

        When _find_fk_ops_for_column_type_changes() emits DROP/ADD FK operations for
        column type changes, table.to() may also emit DROP/ADD for the same constraints
        (e.g. if the constraint definition also changed).  This method strips the duplicates.

        :param alter: An AlterTable operation from table.to()
        :param cycled_fks: Set of (table_name, constraint_name) tuples being cycled
        :returns: The AlterTable with duplicate FK operations removed (or original if no overlap)
        :rtype: AlterTable
        """
        if not cycled_fks:
            return alter

        table_name = alter.table_name
        filtered = AlterTable(table_name)
        for op in alter:
            if isinstance(op, (AddConstraint, RemoveConstraint)):
                constraint_name = op.constraint.name
                if (table_name, constraint_name) in cycled_fks:
                    continue
            filtered.add_operation(op)

        return filtered

    def _find_matching_constraint(self, target_table, source_constraint):
        """Finds a constraint in target_table matching by column/reference, ignoring name.

        :param target_table: The target table to search in
        :param source_constraint: The source constraint to match against
        :returns: The matching target constraint, or None
        :rtype: Constraint|None
        """
        for target_constraint in target_table.constraints.values():
            if (
                target_constraint.column_name == source_constraint.column_name
                and target_constraint.foreign_table_name == source_constraint.foreign_table_name
                and target_constraint.foreign_column_name == source_constraint.foreign_column_name
            ):
                return target_constraint
        return None

    def _column_type_differs(self, source_col, target_col):
        """Checks if two columns differ in their type attributes (type, length, unsigned).

        These are the attributes that MySQL checks for FK compatibility (error 3780).

        :param source_col: The source (live DB) column
        :param target_col: The target (SQL files) column
        :returns: True if the columns differ in type
        :rtype: bool
        """
        if source_col.column_type != target_col.column_type:
            return True
        if source_col.length != target_col.length:
            return True
        if bool(source_col.unsigned) != bool(target_col.unsigned):
            return True
        if source_col.character_set != target_col.character_set:
            return True
        if source_col.collate != target_col.collate:
            return True
        return False
