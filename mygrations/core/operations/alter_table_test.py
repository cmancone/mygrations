import unittest
from .add_index import AddIndex
from .alter_table import AlterTable
from ..definitions.index import Index
from ..definitions.table import Table
from ..definitions.columns import Numeric
class AlterTableTest(unittest.TestCase):
    def test_as_string(self):
        id_column = Numeric('id', 'INT', length=10, unsigned=True, null=False, auto_increment=True)
        user_id_column = Numeric('user_id', 'INT', length=10, unsigned=True, null=False)
        id_index = Index('id', ['id'], 'primary')
        user_id_index = Index('user_id', ['user_id', 'account_id'], 'index')

        alter_table = AlterTable('orders')
        alter_table.add_operation(AddIndex(id_index))
        alter_table.add_operation(AddIndex(user_id_index))

        self.assertEquals(
            "ALTER TABLE `orders` ADD PRIMARY KEY `id` (`id`), ADD KEY `user_id` (`user_id`,`account_id`);",
            str(alter_table)
        )
