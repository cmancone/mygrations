import copy

from mygrations.formats.mysql.definitions.database import database

class mygration:
    """ Creates a migration plan to update a database to a given spec.

    If only one database is passed in, it treats it as a structure to migrate
    to starting from a blank slate, which primariliy means just figuring out
    what order to add tables in to account for foreign key constraints.

    If two tables are present, then it will treat the second as the current
    database constraint, and will figure out steps to execute in action
    to update that second database to match the structure of the first.

    The general steps are:

    1. Add/update columns that exist in both, temporarily skipping FK constraints that aren't yet fulfilled
    2. Remove any foreign keys that don't exist in the target database structure
    3. Add new tables in order necessitated by FK constraints.  Temporarily skip any FK constraints that can't be fulfilled yet
    4. Add in all FKs that were previously skipped
    5. Remove any columns that do not exist in the target database structure, noting an error if a FK is violated
    6. Remove any tables that do not exist in the target database structure, noting an error if a FK is violated
    """
    def __init__( self, db_to, db_from = None ):
        """ Create a migration plan

        :param db_to: The target database structure to migrate to
        :param db_from: The current database structure to migrate from
        :type db_to: mygrations.formats.mysql.definitions.database
        :type db_from: mygrations.formats.mysql.definitions.database
        """

        self.db_to = db_to
        self.db_from = db_from
        [ self._errors_1215, self._operations ] = self._process()

    @property
    def operations( self ):
        """ Public getter.  Returns list of operations to bring db_from to db_to

        If db_from doesn't exist then it will be a list of operations to
        create db_to.

        :returns: A list of table operations
        :rtype: [mygrations.formats.mysql.mygrations.operations.operation]
        """
        return self._operations

    @property
    def errors_1215( self ):
        """ Public getter.  Returns list of 1215 errors (as strings)

        :returns: A list of 1215 error messages
        :rtype: [string]
        """
        return self._errors_1215

    def __len__( self ):
        return len( self._operations )

    def __bool__( self ):
        return True if len( self._operations ) else False

    def __str__( self ):
        return "\n".join( [ str( x ) for x in self._operations ] )

    def __iter__( self ):
        return self._operations.__iter__()

    def _differences(self, a, b):
        """
        Calculates the difference between two OrderedDicts.

        https://codereview.stackexchange.com/a/176303/140581

        Duplication!!!! (formats.mysql.create_parser).  Sue me.

        :param a: OrderedDict
        :param b: OrderedDict
        :return: (added, removed, overlap)
        """

        return (
            [key for key in b if key not in a],
            [key for key in a if key not in b],
            [key for key in a if key in b]
        )

    def _process( self ):
        """ Figures out the operations (and proper order) need to get to self.db_to

        Excessively commented because there are a lot of details and this is a critical
        part of the process
        """

        # Our primary output is a list of operations, but there is more that we need
        # to make all of this happen.  We need a database to keep track of the
        # state of the database we are building after each operation is "applied"
        tracking_db = copy.deepcopy( self.db_from ) if self.db_from else database()

        # First figure out the status of individual tables
        db_from_tables = self.db_from.tables if self.db_from else {}
        ( tables_to_add, tables_to_remove, tables_to_update ) = self._differences( db_from_tables, self.db_to.tables )

        # IMPORTANT! tracking db and tables_to_add are both passed in by reference
        # (like everything in python), but in this case I actually modify them by reference.
        # not my preference, but it makes it easier here
        [ operations, errors_1215 ] = self._process_adds( tracking_db, tables_to_add )

        # if we have errors we are done
        if errors_1215:
            return [ errors_1215, operations ]

        # now apply table updates
        [ more_operations, errors_1215 ] = self._process_updates( tracking_db, tables_to_update )
        operations.extend( more_operations )
        if errors_1215:
            return [ errors_1215, operations ]

        # if we got here all of our tables are acceptable (aka have valid
        # foreign key constraints) but may not have been processed, as
        # there may be mutually-dependent foreign keys, or they may
        # rely upon table modifications (which have not been processed
        # yet).  Handle the table modifications next, then take another
        # go at adding tables.

        # now we have the general todo list, but the reality
        # is much more complicated than that: in particular FK checks.
        # begin straightening it all out!

        # with the straightened out, we just need to check and see what
        # tables might differ
        #operations = []
        #for table in current_tables.intersection( new_tables ):
            #for operation in self.db1.tables[table].to( self.db2.tables[table] ):
                #print( operation )

        # tables to remove must be checked for violations of foreign keys
        # tables to add must be added in proper order for foreign keys
        # foreign keys should probably be added completely separately,
        # although it would be nice to be smart

        return operations

    def _process_adds( tracking_db, tables_to_add ):
        """ Runs through tables_to_add and resolves FK constraints to determine order to add tables in

        tracking_db and tables_to_add are passed in by reference and modified

        :returns: A list of 1215 error messages and a list of mygration operations
        :rtype: [ [string], [mygrations.formats.mysql.mygrations.operations.operation] ]
        """
        errors_1215 = []
        operations = []
        good_tables = {}

        # keep looping through tables as long as we find some to process
        # the while loop will stop under two conditions: if all tables
        # are processed or if we stop adding tables, which happens if we
        # have tables with mutualy-dependent foreign key constraints
        last_number_to_add = 0
        while tables_to_add and len( tables_to_add ) != last_number_to_add:
            last_number_to_add = len( tables_to_add )
            for new_table_name in tables_to_add:
                new_table = self.db_to.tables[new_table_name]
                bad_constraints = tracking_db.unfulfilled_fks( new_table )

                # if we found no problems then we can add this table to our
                # tracking db and add the "CREATE TABLE" operation to our list of operations
                if not bad_constraints:
                    tables_to_add.remove( new_table_name )
                    operations.append( new_table.create() )
                    tracking_db.add_table( new_table )
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
                broken_constraints = self.db_to.unfulfilled_fks( new_table )
                if not broken_constraints:
                    good_tables[new_table_name] = True
                    continue

                # otherwise it is no good: record as such
                is_broken = True
                tables_to_add.remove( new_table_name )
                bad_tables[new_table_name] = broken_constraints
                for error in broken_constraints.values():
                    errors_1215.append( error['error'] )

        return [ errors_1215, operations ]

    def _process_updates( tracking_db, tables_to_update ):
        """ Runs through tables_to_update and resolves FK constraints to determine order to add them in

        tracking_db and tables_to_update are passed in by reference and modified

        :returns: A list of 1215 error messages and a list of mygration operations
        :rtype: [ [string], [mygrations.formats.mysql.mygrations.operations.operation] ]
        """

        errors_1215 = []
        operations = []

        # keep looping through tables as long as we find some to process
        # the while loop will stop under two conditions: if all tables
        # are processed or if we stop adding tables, which happens if we
        # have tables with mutualy-dependent foreign key constraints
        last_number_to_update = 0
        while tables_to_update and len( tables_to_update ) != last_number_to_update:
            last_number_to_update = len( tables_to_update )
            for update_table_name in tables_to_update:
                target_table = self.db_to.tables[update_table_name]
                source_table = self.db_from.tables[update_table_name]

                #########
                ### Pick up here
                more_operations = source_table.to( target_table )
