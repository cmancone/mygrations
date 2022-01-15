class Database:
    _parsing_errors = None
    _schema_errors = None
    _parsing_warnings = None
    _schema_warnings = None
    _tables = None
    _rows = None
    _global_errors = None
    _global_warnings = None

    @property
    def tables(self):
        """ Public getter.  Returns a dict of table definitions, by table name

        :returns: A dict of table definitions, by table name
        :rtype: dict
        """
        return self._tables

    @property
    def rows(self):
        """ Public getter.  Returns a dict of row definitions, by as lists organized by table name

        :returns: A dict of row definitions, by table name
        :rtype: dict[list[Row]]
        """
        return self._rows

    @property
    def errors(self):
        """ Public getter.  Returns a list of errors

        :returns: A list of errors
        :rtype: list
        """
        global_errors = self._global_errors if self._global_errors is not None else []
        schema_errors = self.find_schema_errors()
        parsing_errors = self.find_parsing_errors()
        return [*global_errors, *parsing_errors, *schema_errors]

    @property
    def warnings(self):
        """ Public getter.  Returns a list of warnings

        :returns: A list of warnings
        :rtype: list[string]
        """
        global_warnings = self._global_warnings if self._global_warnings is not None else []
        schema_warnings = self.find_schema_warnings()
        parsing_warnings = self.find_parsing_warnings()
        return [*global_warnings, *parsing_warnings, *schema_warnings]

    def find_schema_warnings(self):
        """ Returns a list of human-readable warning messages (strings) that give any warnings about the schema itself.
        :return: List of warning messages
        :rtype: list
        """
        if self._schema_warnings is not None:
            return self._schema_warnings

        self._schema_warnings = [
            *self.find_all_row_schema_warnings(),
            *self.find_all_table_schema_warnings(),
        ]

        return self._schema_warnings

    def find_schema_errors(self):
        """ Returns a list of human-readable error messages (strings) that give any errors about the schema itself.
        :return: List of error messages
        :rtype: list
        """
        if self._schema_errors is not None:
            return self._schema_errors

        self._schema_errors = [
            *self.find_all_database_schema_errors(),
            *self.find_all_table_schema_errors(),
            *self.find_all_row_schema_errors(),
        ]

        return self._schema_errors

    def find_all_row_schema_errors(self):
        """ Returns a list of any schema error messages for the rows in this database

        :return: A list of schema error messages
        :rtype: list[string]
        """
        errors = []
        for (table_name, rows) in self.rows.items():
            for row in rows:
                if hasattr(row, 'schema_errors'):
                    errors.extend(row.schema_errors)

                # verify the columns which the inserts reference make sense
                if table_name not in self.tables:
                    errors.append(
                        f"Insert error: found an insert for table '{table_name}' but this table does not exist"
                    )

                elif row.num_explicit_columns:
                    table = self.tables[table_name]
                    for column_name in row.columns:
                        if column_name not in table.columns:
                            errors.append(
                                f"Insert error: insert command attempts to set column '{column_name}' for table '{table_name}' but the column does not exist in the table."
                            )
                else:
                    for row_values in row.raw_rows:
                        if len(row_values) != len(table.columns):
                            errors.append(
                                f"Insert error for table '{table_name}': insert command does not explicitly set column names and has a different number of values than the number of columns in the table"
                            )

        return errors

    def find_all_row_schema_warnings(self):
        """ Returns a list of any schema warning messages for the rows in this database

        :return: A list of schema warning messages
        :rtype: list[string]
        """
        warnings = []
        for rows in self.rows.values():
            for row in rows:
                if hasattr(row, 'schema_warnings'):
                    warnings.extend(row.schema_warnings)
        return warnings

    def find_all_table_schema_errors(self):
        """ Returns a list of any schema error messages for the tables in this database

        :return: A list of schema error messages
        :rtype: list[string]
        """
        errors = []
        for table in self.tables.values():
            if hasattr(table, 'schema_errors'):
                errors.extend(table.schema_errors)
        return errors

    def find_all_table_schema_warnings(self):
        """ Returns a list of any schema warnings messages for the tables in this database

        :return: A list of schema warnings messages
        :rtype: list[string]
        """
        warnings = []
        for table in self.tables.values():
            if hasattr(table, 'schema_warnings'):
                warnings.extend(table.schema_warnings)
        return warnings

    def find_all_database_schema_errors(self):
        """ Returns a list of any constraint error messages for this database

        :return: A list of constraint error messages
        :rtype: [string]
        """
        errors = []
        constraint_tables = {}
        for table in self.tables.values():
            if not table.constraints:
                continue

            for constraint in table.constraints.values():
                error = self.find_constraint_errors(table, constraint)
                if error:
                    errors.append(error)

                if constraint.name in constraint_tables:
                    errors.append(
                        f"Duplicate foreign key: foreign key named '{constraint.name}' exists in tables '{constraint_tables[constraint.name]}' and '{table.name}'"
                    )
                else:
                    constraint_tables[constraint.name] = table.name

        return errors

    def find_parsing_errors(self):
        """ Returns a list of human-readable error messages (strings) that give any errors from the parsing process
        :return: List of error messages
        :rtype: list
        """
        if self._parsing_errors is not None:
            return self._parsing_errors

        self._parsing_errors = [
            *self.find_all_table_parsing_errors(),
            *self.find_all_row_parsing_errors(),
        ]

        return self._parsing_errors

    def find_parsing_warnings(self):
        """ Returns a list of human-readable error messages (strings) that give any errors from the parsing process
        :return: List of error messages
        :rtype: list
        """
        if self._parsing_warnings is not None:
            return self._parsing_warnings

        self._parsing_warnings = [
            *self.find_all_table_parsing_warnings(),
            *self.find_all_row_parsing_warnings(),
        ]

        return self._parsing_warnings

    def find_all_table_parsing_errors(self):
        """ Returns a list of human-readable error messages (strings) from the table parsing process
        :return: List of error messages
        :rtype: list
        """
        errors = []
        for table in self.tables.values():
            if hasattr(table, 'parsing_errors'):
                errors.extend(table.parsing_errors)
        return errors

    def find_all_row_parsing_errors(self):
        """ Returns a list of human-readable error messages (strings) from the row parsing process
        :return: List of error messages
        :rtype: list
        """
        errors = []
        for (table_name, rows) in self.rows.items():
            for row in rows:
                if hasattr(row, 'parsing_errors'):
                    errors.extend(row.parsing_errors)
        return errors

    def find_all_table_parsing_warnings(self):
        """ Returns a list of human-readable warning messages (strings) from the table parsing process
        :return: List of warning messages
        :rtype: list
        """
        warnings = []
        for table in self.tables.values():
            if hasattr(table, 'parsing_warnings'):
                warnings.extend(table.parsing_warnings)
        return warnings

    def find_all_row_parsing_warnings(self):
        """ Returns a list of human-readable warning messages (strings) from the row parsing process
        :return: List of warning messages
        :rtype: list
        """
        warnings = []
        for (table_name, rows) in self.rows.items():
            for row in rows:
                if hasattr(table, 'parsing_warnings'):
                    warnings.extend(row.parsing_warnings)
        return warnings

    def find_constraint_errors(self, table, constraint):
        """ Returns None or a string with an error message for the given table and constraint

        :param table: The table being checked
        :param constraint: The constraint to check the table against
        :type table: mygrations.core.definitions.table
        :type constraint: mygrations.core.definitions.constraint
        :rtype: string|None
        """

        if constraint.foreign_table_name not in self.tables:
            return "Constraint error for foreign key `%s`: `%s`.`%s` references `%s`.`%s`, but table `%s` does not exist" % (
                constraint.name, table.name, constraint.column_name, constraint.foreign_table_name,
                constraint.foreign_column_name, constraint.foreign_table_name
            )
        foreign_table = self.tables[constraint.foreign_table_name]
        if constraint.foreign_column_name not in foreign_table.columns:
            return "Constraint error for foreign key `%s`: `%s`.`%s` references `%s`.`%s`, but column `%s`.`%s` does not exist" % (
                constraint.name, table.name, constraint.column_name, constraint.foreign_table_name,
                constraint.foreign_column_name, constraint.foreign_table_name, constraint.foreign_column_name
            )

        # the column exists but we may still have a constraint error.  That can happen in a few ways
        if constraint.column_name not in table.columns:
            return "Constraint error for foreign key `%s`: sets constraint on column `%s`.`%s`, but this column does not exist" % (
                constraint.name, table.name, constraint.column_name
            )
        table_column = table.columns[constraint.column_name]
        foreign_column = foreign_table.columns[constraint.foreign_column_name]

        if not table.column_is_indexed(table.columns[table_column.name]):
            return "Constraint error for foreign key `%s`: missing index. `%s`.`%s` does not have an index and therefore cannot be used in a foreign key constraint" % (
                constraint.name, table.name, table_column.name
            )

        # we have a few attributes that must must match exactly and have easy-to-produce errors
        for attr in ['column_type', 'length', 'character_set', 'collate']:
            table_value = getattr(table_column, attr)
            foreign_value = getattr(foreign_column, attr)
            if table_value != foreign_value:
                return "Constraint error for foreign key `%s`: %s mismatch. `%s`.`%s` is '%s' but `%s`.`%s` is '%s'" % (
                    constraint.name, attr.replace('_', ' '), table.name, constraint.column_name, table_value,
                    foreign_table.name, foreign_column.name, foreign_value
                )

        # unsigned are separate because they get a slightly different message
        if table_column.unsigned and not foreign_column.unsigned:
            return "Constraint error for foreign key `%s`: unsigned mistmatch. `%s`.`%s` is unsigned but `%s`.`%s` is not" % (
                constraint.name, table.name, table_column.name, foreign_table.name, foreign_column.name
            )

        if not table_column.unsigned and foreign_column.unsigned:
            return "Constraint error for foreign key `%s`: unsigned mistmatch. `%s`.`%s` is unsigned but `%s`.`%s` is not" % (
                constraint.name, foreign_table.name, foreign_column.name, table.name, table_column.name
            )

        # if the constraint has a SET NULL but the column cannot be null, then 1215
        if (constraint.on_delete == 'SET NULL' or constraint.on_update == 'SET NULL') and not table_column.null:
            message_parts = []
            if constraint.on_delete == 'SET NULL':
                message_parts.append('ON DELETE')
            if constraint.on_update == 'SET NULL':
                message_parts.append('ON UPDATE')
            return "Constraint error for foreign key `%s`: invalid SET NULL. `%s`.`%s` is not allowed to be null but the foreign key attempts to set the value to null %s" % (
                constraint.name, table.name, table_column.name, ' and '.join(message_parts)
            )

        # if the column the constraint is on doesn't have an index, then 1215
        if not foreign_table.column_is_indexed(foreign_column):
            return "Constraint error for foreign key `%s`: missing index. `%s`.`%s` references `%s`.`%s` but `%s`.`%s` does not have an index and therefore cannot be used in a foreign key constraint" % (
                constraint.name, table.name, table_column.name, foreign_table.name, foreign_column.name,
                foreign_table.name, foreign_column.name
            )

        return None

    def unfulfilled_fks(self, table):
        """ Returns a dictionary with information about all constraints in the table which are not fulfilled by this database

        If all foreign keys are fulfilled by the database structure then an empty dict is returned

        The returned dictionary contains a key with the name of every foreign key that cannot
        be fulfilled.  The value in the dictionary will be another dictionary containing
        'error' (an error message stating exactly what the problem is) and 'foreign_key'
        (the actual foreign key definition that cannot be fulfilled).

        This is similar to find_all_database_schema_errors but is used in a specific way by the migration process,
        so gets its own method (although both rely heavily on the `find_constraint_errors` method.

        :param table: The table to check
        :type table: mygrations.formats.mysql.definitions.table
        :return: Dictionary with information on all foreign keys that cannot be fulfilled
        :rtype: dict
        """
        if not table.constraints:
            return {}

        unfulfilled = {}
        for (constraint_name, constraint) in table.constraints.items():
            error = self.find_constraint_errors(table, constraint)
            if error:
                unfulfilled[constraint_name] = {"error": error, "foreign_key": constraint}

        return unfulfilled

    def add_table(self, table):
        """ Adds a table to the database

        :param table: The table to add
        :type table: mygrations.formats.mysql.definitions.table
        """
        if table.name in self._tables:
            raise ValueError('Cannot add table %s to database because it already exists' % table.name)

        self._schema_errors = None
        self._schema_warnings = None
        self._tables[table.name] = table

    def remove_table(self, table):
        """ Removes a table from the database

        :param table: The table to remove
        :type table: mygrations.formats.mysql.definitions.table
        """
        if not table.name in self._tables:
            raise ValueError('Cannot remove table %s from database because it does not exist' % table.name)

        self._schema_errors = None
        self._schema_warnings = None
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
        self._schema_errors = None
        self._schema_warnings = None
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
