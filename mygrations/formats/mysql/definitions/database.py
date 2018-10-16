class database(object):

    _errors = None
    _warnings = None
    _tables = None
    _rows = None
    _errors_1215 = None

    def __init__(self):
        self._warnings = []
        self._errors = []
        self._tables = {}
        self._rows = []
        self._errors_1215 = None

    @property
    def tables(self):
        """ Public getter.  Returns a dict of table definitions, by table name

        :returns: A dict of table definitions, by table name
        :rtype: dict
        """
        return self._tables

    @property
    def errors(self):
        """ Public getter.  Returns a list of parsing errors

        :returns: A list of parsing errors
        :rtype: list
        """
        return self._errors

    @property
    def warnings(self):
        """ Public getter.  Returns a list of parsing/table warnings

        :returns: A list of parsing/table warnings
        :rtype: list
        """
        return self._warnings

    @property
    def errors_1215(self):
        """ Public getter.  Returns a list of 1215 errors found for the database

        :returns: A list of MySQL 1215 error messages
        :rtype: [string]
        """
        if self._errors_1215 is None:
            self._errors_1215 = self._find_all_1215_errors()
        return self._errors_1215

    def store_rows_with_tables(self):
        """ Processes table rows and adds them to the appropriate tables

        Table rows are stored with tables for comparison purposes, but might
        come in through their own separate files.  This method puts the two
        together.
        """
        for rows in self._rows:
            if not rows.table in self._tables:
                self._errors.append('Found rows for table %s but that table does not have a definition' % rows.table)
                continue

            returned = self._tables[rows.table].add_rows(rows)
            if isinstance(returned, str):
                self._errors.append(returned)

    def unfulfilled_fks(self, table):
        """ Returns a dictionary with information about all constraints in the table which are not fulfilled by this database

        If all foreign keys are fulfilled by the database structure then an empty dict is returned

        The returned dictionary contains a key with the name of every foreign key that cannot
        be fulfilled.  The value in the dictionary will be another dictionary containing
        'error' (an error message stating exactly what the problem is) and 'foreign_key'
        (the actual foreign key definition that cannot be fulfilled)

        :param table: The table to check
        :type table: mygrations.formats.mysql.definitions.table
        :return: Dictionary with information on all foreign keys that cannot be fulfilled
        :rtype: dict
        """
        if not table.constraints:
            return {}

        unfulfilled = {}
        for (constraint_name, constraint) in table.constraints.items():
            error = self.find_1215_errors(table, constraint)
            if error:
                unfulfilled[constraint_name] = {"error": error, "foreign_key": constraint}

        return unfulfilled

    def _find_all_1215_errors(self):
        """ Returns a list of any 1215 error messages for this database

        :return: A list of 1215 error messages
        :rtype: [string]
        """
        errors = []
        for table in self.tables.values():
            if not table.constraints:
                continue

            for constraint in table.constraints.values():
                error = self.find_1215_errors(table, constraint)
                if error:
                    errors.append(error)

        return errors

    def find_1215_errors(self, table, constraint):
        """ Returns None or a string describing a 1215 error message found for the given table and constraint

        :param table: The table being checked
        :param constraint: The constraint to check the table against
        :type table: mygrations.formats.mysql.definitions.table
        :type constraint: mygrations.formats.mysql.definitions.constraint
        :rtype: string|None
        """

        if constraint.foreign_table not in self.tables:
            return "MySQL 1215 error for foreign key `%s`: `%s`.`%s` references `%s`.`%s`, but table `%s` does not exist" % (
                constraint.name, table.name, constraint.column, constraint.foreign_table, constraint.foreign_column,
                constraint.foreign_table
            )
        foreign_table = self.tables[constraint.foreign_table]
        if constraint.foreign_column not in foreign_table.columns:
            return "MySQL 1215 error for foreign key `%s`: `%s`.`%s` references `%s`.`%s`, but column `%s`.`%s` does not exist" % (
                constraint.name, table.name, constraint.column, constraint.foreign_table, constraint.foreign_column,
                constraint.foreign_table, constraint.foreign_column
            )

        # the column exists but we may still have a 1215 error.  That can happen in a few ways
        table_column = table.columns[constraint.column]
        foreign_column = foreign_table.columns[constraint.foreign_column]

        if not table.column_is_indexed(table.columns[table_column.name]):
            return "MySQL 1215 error for foreign key `%s`: missing index. `%s`.`%s` does not have an index and therefore cannot be used in a foreign key constraint" % (
                constraint.name, table.name, table_column.name
            )

        # we have a few attributes that must must match exactly and have easy-to-produce errors
        for attr in ['column_type', 'length', 'character_set', 'collate']:
            table_value = getattr(table_column, attr)
            foreign_value = getattr(foreign_column, attr)
            if table_value != foreign_value:
                return "MySQL 1215 error for foreign key `%s`: %s mismatch. `%s`.`%s` is '%s' but `%s`.`%s` is '%s'" % (
                    constraint.name, attr.replace('_', ' '), table.name, constraint.column, table_value,
                    foreign_table.name, foreign_column.name, foreign_value
                )

        # unsigned are separate because they get a slightly different message
        if table_column.unsigned and not foreign_column.unsigned:
            return "MySQL 1215 error for foreign key `%s`: unsigned mistmatch. `%s`.`%s` is unsigned but `%s`.`%s` is not" % (
                constraint.name, table.name, table_column.name, foreign_table.name, foreign_column.name
            )

        if not table_column.unsigned and foreign_column.unsigned:
            return "MySQL 1215 error for foreign key `%s`: unsigned mistmatch. `%s`.`%s` is unsigned but `%s`.`%s` is not" % (
                constraint.name, foreign_table.name, foreign_column.name, table.name, table_column.name
            )

        # if the constraint has a SET NULL but the column cannot be null, then 1215
        if (constraint.on_delete == 'SET NULL' or constraint.on_update == 'SET NULL') and not table_column.null:
            message_parts = []
            if constraint.on_delete == 'SET NULL':
                message_parts.append('ON DELETE')
            if constraint.on_update == 'SET NULL':
                message_parts.append('ON UPDATE')
            return "MySQL 1215 error for foreign key `%s`: invalid SET NULL. `%s`.`%s` is not allowed to be null but the foreign key attempts to set the value to null %s" % (
                constraint.name, table.name, table_column.name, ' and '.join(message_parts)
            )

        # if the column the constraint is on doesn't have an index, then 1215
        if not foreign_table.column_is_indexed(foreign_column):
            return "MySQL 1215 error for foreign key `%s`: missing index. `%s`.`%s` references `%s`.`%s` but `%s`.`%s` does not have an index and therefore cannot be used in a foreign key constraint" % (
                constraint.name, table.name, table_column.name, foreign_table.name, foreign_column.name,
                foreign_table.name, foreign_column.name
            )

        return None

    def add_table(self, table):
        """ Adds a table to the database

        :param table: The table to add
        :type table: mygrations.formats.mysql.definitions.table
        """
        if table.name in self._tables:
            raise ValueError('Cannot add table %s to database because it already exists' % table.name)

        self._errors_1215 = None
        self._tables[table.name] = table

    def remove_table(self, table):
        """ Removes a table from the database

        :param table: The table to remove
        :type table: mygrations.formats.mysql.definitions.table
        """
        if not table.name in self._tables:
            raise ValueError('Cannot remove table %s from database because it does not exist' % table.name)

        self._errors_1215 = None
        self._tables.pop(table.name, None)

    def apply_operation(self, table_name, operation):
        """ Updates the database object according to the operation

        :param table_name: The table that the operation is being applied to
        :param operation: The operation to apply
        :type table: string|mygrations.formats.mysql.definitions.table
        :type operation: mygrations.formats.mysql.mygration.operations.*
        """
        if type(table_name) != str:
            table_name = table_name.name

        if not table_name in self._tables:
            raise ValueError('Cannot apply operation to table %s because that table does not exist' % table_name)

        # the table applies the operation
        self._errors_1215 = None
        self._tables[table_name].apply_operation(operation)

    def apply_to_source(self, operation):
        """ Updates the actual source of the database object: usually the database or a .sql file

        This method and :meth:`mygrations.formats.mysql.defintions.database.apply_operation` sound very similar.
        The difference is that the latter operates on the in-memory structure store only, and makes
        no actual changes.  Instead it is primarily used for internal purposes.  This method actually
        makes changes.

        :param operation: The operation to apply
        :type operation: mygrations.formats.mysql.mygration.operations.*
        """
        raise NotImplementedError("Someone forgot to finish something")
