import unittest
from .create_table import CreateTable
from ..definitions.columns import String, Numeric
from ..definitions.index import Index
from ..definitions.table import Table
from ..definitions.option import Option
class CreateTableTest(unittest.TestCase):
    def test_as_string(self):
        table = Table(
            'test_table', [
                Numeric('id', 'INT', length=10, unsigned=True, auto_increment=True),
                String('name', 'VARCHAR', length=255)
            ], [Index('id', ['id'], 'PRIMARY')], [], [Option('ENGINE', 'InnoDB')]
        )
        self.assertEquals(
            """CREATE TABLE `test_table` (
  `id` INT(10) UNSIGNED AUTO_INCREMENT,
  `name` VARCHAR(255),
  PRIMARY KEY `id` (`id`)
) ENGINE=InnoDB;""", str(CreateTable(table, True))
        )
        self.assertEquals(
            """CREATE TABLE `test_table` (`id` INT(10) UNSIGNED AUTO_INCREMENT,`name` VARCHAR(255),PRIMARY KEY `id` (`id`)) ENGINE=InnoDB;""",
            str(CreateTable(table, False))
        )
