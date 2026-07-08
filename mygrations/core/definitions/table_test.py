import unittest
from collections import OrderedDict
from .columns import Numeric, String
from .constraint import Constraint
from .index import Index
from .option import Option
from .table import Table


class TestTable(unittest.TestCase):
    def setUp(self):
        self.id = Numeric("id", "INT", length=10, unsigned=True, null=False, auto_increment=True)
        self.user_id = Numeric("user_id", "INT", length=10, unsigned=True, null=True)
        self.age = Numeric("age", "INT", length=10, unsigned=True, default=0)
        self.name = String("name", "VARCHAR", length=255, default="", null=False)
        self.id_index = Index("id_index", ["id"], "PRIMARY")
        self.name_age_index = Index("name_age", ["name", "age"], "INDEX")
        self.user_id_index = Index("user_id_index", ["user_id"], "INDEX")
        self.user_id_constraint = Constraint("user_id_fk", "user_id", "users", "id", "SET NULL", "SET NULL")
        self.engine = Option("ENGINE", "InnoDB")

    def test_can_create(self):
        table = Table(
            "registrations",
            [self.id, self.user_id, self.age, self.name],
            [self.id_index, self.name_age_index, self.user_id_index],
            [self.user_id_constraint],
            [self.engine],
        )

        self.assertEqual("registrations", table.name)
        self.assertEqual(["id", "user_id", "age", "name"], [column.name for column in table.columns.values()])
        self.assertEqual(["user_id_fk"], [constraint.name for constraint in table.constraints.values()])
        self.assertEqual(["id_index", "name_age", "user_id_index"], [index.name for index in table.indexes.values()])
        self.assertEqual([self.engine], table.options)
        self.assertEqual(self.id_index, table.primary)
        self.assertEqual([], table.schema_errors)
        self.assertEqual([], table.schema_warnings)

    def test_require_basics(self):
        table = Table("", [self.id], [self.id_index], [], [])
        self.assertEqual(["Table missing name"], table.schema_errors)

        table = Table("no_cols", [], [], [], [])
        self.assertEqual(["Table 'no_cols' does not have any columns"], table.schema_errors)

    def test_include_child_errors(self):
        bad_column = String("text", "TEXT", default="", has_default=True)
        bad_index = Index("no_cols", [], "INDEX")
        bad_constraint = Constraint("user_id_fk", "user_id", "users", "id", on_delete="CASCAD")
        table = Table(
            "errors",
            [self.id, self.user_id, bad_column],
            [self.id_index, bad_index],
            [bad_constraint],
            [self.engine],
        )
        self.assertEqual(
            [
                "Column 'text' of type 'TEXT' cannot have a default in table 'errors'",
                "Missing columns for index no_cols in table 'errors'",
                "ON DELETE action of 'CASCAD' for constraint 'user_id_fk' is not a valid ON DELETE action in table 'errors'",
            ],
            table.schema_errors,
        )

    def test_check_primaries(self):
        table = Table("errors", [self.id], [self.id_index, Index("id_primary", ["id"], "PRIMARY")], [], [])
        self.assertEqual(["Table 'errors' has more than one PRIMARY index"], table.schema_errors)

        table = Table("errors", [self.id], [], [], [])
        self.assertEqual(
            ["Table 'errors' has an AUTO_INCREMENT column but is missing the PRIMARY index"], table.schema_errors
        )

        table = Table(
            "errors",
            [self.id, self.user_id],
            [Index("user_id", ["user_id"], "PRIMARY")],
            [],
            [],
        )
        self.assertEqual(
            [
                "Mismatched indexes in table 'errors': column 'id' is the AUTO_INCREMENT column but 'user_id' is the PRIMARY index column"
            ],
            table.schema_errors,
        )

    def test_check_missing_index_columns(self):
        table = Table(
            "errors", [self.id, self.user_id], [self.id_index, Index("bad_index", ["non_column"], "INDEX")], [], []
        )
        self.assertEqual(
            ["Table 'errors' has index 'bad_index' that references non-existent column 'non_column'"],
            table.schema_errors,
        )

    def test_no_warning_for_primary_key_without_default(self):
        pk_col = Numeric("id", "INT", length=10, unsigned=True, null=False)
        pk_index = Index("PRIMARY", ["id"], "PRIMARY")
        table = Table("test_table", [pk_col], [pk_index], [], [])
        self.assertEqual([], table.schema_warnings)

    def test_warning_for_non_pk_column_without_default(self):
        pk_col = Numeric("id", "INT", length=10, unsigned=True, null=False, auto_increment=True)
        data_col = Numeric("status", "INT", null=False)
        pk_index = Index("PRIMARY", ["id"], "PRIMARY")
        table = Table("test_table", [pk_col, data_col], [pk_index], [], [])
        self.assertEqual(
            [
                "Column status does not allow null values and has no default: you should set a default to avoid warnings in table 'test_table'"
            ],
            table.schema_warnings,
        )
