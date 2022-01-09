import copy

from mygrations.formats.mysql.definitions.database import Database
from mygrations.formats.mysql.mygrations.operations.alter_table import AlterTable
from mygrations.formats.mysql.mygrations.operations.add_constraint import AddConstraint
from mygrations.formats.mysql.mygrations.operations.remove_table import RemoveTable
from mygrations.formats.mysql.mygrations.operations.disable_checks import DisableChecks
from mygrations.formats.mysql.mygrations.operations.enable_checks import EnableChecks
class Mygration:
    """ Creates a migration plan to update a database to a given spec.

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
        """ Create a migration plan

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
        """ Public getter.  Returns list of operations to bring db_from to db_to

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
        """ Public getter.  Returns list of 1215 errors (as strings)

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

        return ([key for key in to_dict if key not in from_dict], [key for key in from_dict if key not in to_dict],
                [key for key in from_dict if key in to_dict])

    def _process(self):
        """ Figures out the operations needed to get to self.db_to

        Returns a list of operations that will migrate db_from to db_to

        For performance reasons the migrations are done with foreign key
        checks off: the first operation turns them off, and the last operation
        turns them on.

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

        for table_name in tables_to_update:
            target_table = self.db_to.tables[table_name]
            source_table = self.db_from.tables[table_name]
            operations.extend(source_table.to(target_table))

        for table_name in tables_to_remove:
            operations.append(RemoveTable(table_name))

        if self._disable_fk_checks:
            operations.append(EnableChecks())

        return operations

    def _old_process(self):
        """ Figures out the operations (and proper order) need to get to self.db_to

        This particular method is no longer used but is kept around for future
        reference.  This was my original attempt, the goal of which was to make the
        system smart enough to determine the proper order of operations to avoid
        violating FK constraints.  See these:

        https://codereview.stackexchange.com/q/177780/140581
        https://softwareengineering.stackexchange.com/q/359107/243180

        However, based primarly on concerns about performance, I've decided to
        let it be dumb and simply perform all operations with FK
        checking off, and then turn it back on when done.  I'm going to leave this
        here though because I may resurrect it with a flag to enable migrations
        with FK checks on.  When I do that though it will be time to figure out
        proper topological sorting

        Excessively commented because there are a lot of details and this is a critical
        part of the process
        """

        # Our primary output is a list of operations, but there is more that we need
        # to make all of this happen.  We need a database to keep track of the
        # state of the database we are building after each operation is "applied"
        tracking_db = copy.deepcopy(self.db_from) if self.db_from else Database()

        # a little bit of extra processing will simplify our algorithm by a good chunk.
        # The situation is much more complicated when we have a database we are migrating
        # from, because columns might be added/removed/changed, and it might be (for instance)
        # that the removal of a column breaks a foreign key constraint.  The general
        # ambiguities introduced by changes happening in different times/ways makes it
        # much more difficult to figure out when foreign key constraints can properly
        # be added without triggering a 1215 error.  The simplest way to straighten this
        # all out is to cheat: "mygrate" the "to" database all by itself.  Without a "from"
        # the operations are more straight-forward, and we can figure out with less effort
        # whether or not all FK constraints can be fulfilled.  If they aren't all fulfilled,
        # then just quit now before we do anything.  If they are all fulfilled then we
        # know our final table will be fine, so if we can just split off any uncertain
        # foreign key constraints and apply them all at the end when our database is done
        # being updated.  Simple(ish)!
        #if self.db_from:
        #check = mygration( self.db_to )
        #if check.errors_1215:
        #return [ check.errors_1215, [] ]

        # First figure out the status of individual tables
        db_from_tables = self.db_from.tables if self.db_from else {}
        (tables_to_add, tables_to_remove, tables_to_update) = self._differences(db_from_tables, self.db_to.tables)

        # IMPORTANT! tracking db and tables_to_add are both passed in by reference
        # (like everything in python), but in this case I actually modify them by reference.
        # not my preference, but it makes it easier here
        (errors_1215, operations) = self._process_adds(tracking_db, tables_to_add)

        # if we have errors we are done
        #if errors_1215:
        #return [ errors_1215, operations ]

        # now apply table updates.  This acts differently: it returns a dictionary with
        # two sets of operations: one to update the tables themselves, and one to update
        # the foreign keys.  The latter are applied after everything else has happened.
        fk_operations = []
        split_operations = self._process_updates(tracking_db, tables_to_update)
        # remove fks first to avoid 1215 errors caused by trying to remove a column
        # that is being used in a FK constraint that hasn't yet been removed
        if split_operations['removed_fks']:
            operations.extend(split_operations['removed_fks'])
        if split_operations['kitchen_sink']:
            operations.extend(split_operations['kitchen_sink'])
        if split_operations['fks']:
            fk_operations.extend(split_operations['fks'])

        # now that we got some tables modified let's try adding tables again
        # if we have any left.  Remember that tracking_db and tables_to_add
        # are modified in-place.  The point here is that there may be some
        # tables to add that we were not able to add before because they
        # relied on adding a column to a table before a foreign key could
        # be supported.
        if tables_to_add:
            (errors_1215, more_operations) = self._process_adds(tracking_db, tables_to_add)
            if more_operations:
                operations = operations.extend(more_operations)
            if errors_1215:
                if fk_operations:
                    operations.extend(fk_operations)
                return operations

        # At this point in time if we still have tables to add it is because
        # they have mutually-dependent foreign key constraints.  The way to
        # fix that is to be a bit smarter (but not too smart) and remove
        # from the tables all foreign key constraints that can't be added yet.
        # Then run the CREATE TABLE operations, and add the foreign key
        # constraints afterward
        for table_to_add in tables_to_add:
            new_table = self.db_to.tables[table_to_add]
            bad_constraints = tracking_db.unfulfilled_fks(new_table)
            new_table_copy = copy.deepcopy(new_table)
            create_fks = AlterTable(table_to_add)
            for constraint in bad_constraints.values():
                create_fks.add_operation(AddConstraint(constraint['foreign_key']))
                new_table_copy.remove_constraint(constraint['foreign_key'])
            operations.append(new_table_copy.create())
            fk_operations.append(create_fks)

        # process any remaining foreign key constraints
        if fk_operations:
            operations.extend(fk_operations)

        # finally remove any tables
        for table_to_remove in tables_to_remove:
            operations.append(RemoveTable(table_to_remove))
            tracking_db.remove_table(table_to_remove)

        # all done!!!
        return operations

    def _process_adds(self, tracking_db, tables_to_add):
        """ Runs through tables_to_add and resolves FK constraints to determine order to add tables in

        tracking_db and tables_to_add are passed in by reference and modified

        :returns: A list of 1215 error messages and a list of mygration operations
        :rtype: ( [{'error': string, 'foreign_key': mygrations.formats.mysql.definitions.constraint}], [mygrations.formats.mysql.mygrations.operations.operation] )
        """
        errors_1215 = []
        operations = []
        good_tables = {}

        # keep looping through tables as long as we find some to process
        # the while loop will stop under two conditions: if all tables
        # are processed or if we stop adding tables, which happens if we
        # have tables with mutualy-dependent foreign key constraints
        last_number_to_add = 0
        while tables_to_add and len(tables_to_add) != last_number_to_add:
            last_number_to_add = len(tables_to_add)
            for new_table_name in tables_to_add:
                new_table = self.db_to.tables[new_table_name]
                bad_constraints = tracking_db.unfulfilled_fks(new_table)

                # if we found no problems then we can add this table to our
                # tracking db and add the "CREATE TABLE" operation to our list of operations
                if not bad_constraints:
                    tables_to_add.remove(new_table_name)
                    operations.append(new_table.create())
                    tracking_db.add_table(new_table)
                    continue

                # the next question is whether this is a valid constraint
                # that simply can't be added yet (because it has dependencies
                # that have not been added) or if there is an actual problem
                # with the constraint.
                if new_table_name in good_tables:
                    continue

                # If we are here we have to decide if this table is fulfillable
                # eventually, or if there is a mistake with a foreign key that
                # we can't fix.  To tell the difference we just check if the
                # database we are migrating to can fulfill these foreign keys.
                broken_constraints = self.db_to.unfulfilled_fks(new_table)
                if not broken_constraints:
                    good_tables[new_table_name] = True
                    continue

                # otherwise it is no good: record as such
                tables_to_add.remove(new_table_name)
                for error in broken_constraints.values():
                    errors_1215.append(error['error'])

        return (errors_1215, operations)

    def _process_updates(self, tracking_db, tables_to_update):
        """ Runs through tables_to_update and resolves FK constraints to determine order to add them in

        tracking_db is passed in by reference and modified

        This doesn't return a list of 1215 errors because those would have been
        Taken care of the first run through when the "to" database was mygrated
        by itself.  Instead, this separates alters and addition/modification of
        foreign key updates into different operations so the foreign key updates
        can be processed separately.

        :returns: a dict
        :rtype: {'fks': list, 'kitchen_sink': list}
        """

        tables_to_update = tables_to_update[:]

        operations = {'removed_fks': [], 'fks': [], 'kitchen_sink': []}

        for update_table_name in tables_to_update:
            target_table = self.db_to.tables[update_table_name]
            source_table = self.db_from.tables[update_table_name]

            more_operations = source_table.to(target_table, True)
            if 'removed_fks' in more_operations:
                operations['removed_fks'].append(more_operations['removed_fks'])
                for operation in more_operations['removed_fks']:
                    tracking_db.apply_operation(update_table_name, operation)
            if 'fks' in more_operations:
                operations['fks'].append(more_operations['fks'])
                for operation in more_operations['fks']:
                    tracking_db.apply_operation(update_table_name, operation)
            if 'kitchen_sink' in more_operations:
                operations['kitchen_sink'].append(more_operations['kitchen_sink'])
                for operation in more_operations['kitchen_sink']:
                    tracking_db.apply_operation(update_table_name, operation)

        return operations
