import unittest

from mygrations.formats.mysql.file_reader.database import Database as DatabaseReader
class test_table_1215_regressions(unittest.TestCase):
    def test_foreign_key_without_index(self):
        """ Discovered that the system was not raising an error for a foreign key that didn't have an index for the table it was attached to """

        db = DatabaseReader([
            """CREATE TABLE `vendors` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT, PRIMARY KEY (`id`));""",
            """CREATE TABLE `payment_requests_external` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `account_id` int(10) UNSIGNED NOT NULL,
  `vendor_id` int(10) UNSIGNED DEFAULT NULL,
  `vendor_name` VARCHAR(255) NOT NULL DEFAULT '',
  `vendor_city` VARCHAR(255) NOT NULL DEFAULT '',
  `vendor_state` VARCHAR(255) NOT NULL DEFAULT '',
  `vendor_zip` VARCHAR(255) NOT NULL DEFAULT '',
  `vendor_list_id` VARCHAR(255) NOT NULL DEFAULT '',
  `edit_sequence` VARCHAR(255) NOT NULL DEFAULT '',
  `memo` VARCHAR(255) NOT NULL DEFAULT '',
  `request_date` INT(10) UNSIGNED NOT NULL DEFAULT 0,
  `guid` VARCHAR(255) NOT NULL DEFAULT '',
  `po_number` VARCHAR(255) NOT NULL DEFAULT '',
  `description` VARCHAR(255) NOT NULL DEFAULT '',
  `property_address1` VARCHAR(255) NOT NULL DEFAULT '',
  `property_address2` VARCHAR(255) NOT NULL DEFAULT '',
  `property_city` VARCHAR(255) NOT NULL DEFAULT '',
  `property_state` VARCHAR(255) NOT NULL DEFAULT '',
  `property_zip` VARCHAR(255) NOT NULL DEFAULT '',
  `customer_name` VARCHAR(255) NOT NULL DEFAULT '',
  `customer_list_id` VARCHAR(255) NOT NULL DEFAULT '',
  `contractor_completion_date` INT(10) UNSIGNED NOT NULL,
  `po_amount` DECIMAL(20,2) NOT NULL,
  `line_items` text,
  created INT(10) UNSIGNED NOT NULL DEFAULT 0,
  updated INT(10) UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `account_id_pr_external` (`account_id`),
  CONSTRAINT `vendor_id_pr_external_fk` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;"""
        ])

        self.assertEquals(1, len(db.errors))
        self.assertEquals(
            'Constraint error for foreign key `vendor_id_pr_external_fk`: missing index. `payment_requests_external`.`vendor_id` does not have an index and therefore cannot be used in a foreign key constraint',
            db.errors[0]
        )
