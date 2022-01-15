import unittest

from mygrations.formats.mysql.file_reader.reader import Reader
from mygrations.formats.mysql.file_reader.database import Database
class RegressionTest(unittest.TestCase):
    """ Some tests based off failing CREATE TABLE commands from our database when things were first being finished """
    def test_payment_request_types(self):

        parser = Reader()
        returned = parser.parse(
            """CREATE TABLE `payment_request_types` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `slug` VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `order_by` INT(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `order_by_payment_request_types` (`order_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO payment_request_types (id,name,slug,order_by) VALUES (1,'Standard','standard',1),(2,'Special Circumstances','emergency',2);"""
        )

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have matched everything
        self.assertEquals('', returned)

        # we should not have any errors
        self.assertEquals([], parser.schema_errors)
        self.assertEquals([], parser.parsing_errors)

    def test_employee_contract_list(self):

        db = Database(
            """CREATE TABLE `employee_contract_list` (
 `id` int(10) NOT NULL AUTO_INCREMENT,
 `account_id` int(10) unsigned NOT NULL,
 `name` varchar(255) NOT NULL,
 `display` varchar(255) NOT NULL,
 `table_name` varchar(255) NOT NULL,
 `employee_field_name` varchar(255) NOT NULL,
 `link` varchar(255) NOT NULL,
 PRIMARY KEY (`id`),
 KEY `employee_contact_list_account_id_ref_accounts_id` (`account_id`),
 CONSTRAINT `employee_contact_list_account_id_ref_accounts_id` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `employee_contract_list` (`id`, `account_id`, `name`, `display`, `table_name`, `employee_field_name`, `link`) VALUES
(1, 1, 'main_contract', 'Employee Contract', 'employee_main_contracts', 'main_contract_id', 'hr/contracts/sign_main_contract'),
(2, 1, 'nda', 'Non-Disclosure Agreement ', 'employee_ndas', 'nda_id', 'hr/contracts/sign_nda'),
(3, 1, 'non_compete', 'Employee No Compete Agreement', 'employee_no_competes', 'no_compete_id', 'hr/contracts/complete_non_compete'),
(4, 1, 'dd_auth', 'Direct Deposit Authorization', 'employee_dd_auths', 'dd_auth_id', 'hr/contracts/complete_dd_auth'),
(5, 1, 'property_agreement', 'Company Property Return/Receipt', 'employee_property_agrees', 'property_receipt_id', 'hr/contracts/property_agreement'),
(6, 1, 'background_ck_agreement', 'Background Check Agreement', 'employee_background_ck_releases', 'background_ck_id', 'hr/contracts/background_ck_agreement'),
(7, 1, 'employee_handbook', 'Employee Handbook Receipt', 'employee_handbook_receipts', 'handbook_receipt_id', 'hr/contracts/sign_employee_handbook'),
(8, 1, 'cell_phone_policy', 'Company Cell Phone Policy', 'employee_cell_policy_receipts', 'cell_policy_receipt_id', 'hr/contracts/sign_cell_phone_policy'),
(9, 1, 'fed_w4', 'Federal W-4', 'employee_fed_w4s', 'fed_w4_id', 'hr/tax_forms/complete_fed_w4'),
(10, 1, 'ga_w4', 'Georgia W-4', 'employee_ga_w4s', 'ga_w4_id', 'hr/tax_forms/complete_ga_w4'),
(11, 1, 'al_a4', 'Alabama A-4', 'employee_al_a4s', 'al_w4_id', 'hr/tax_forms/complete_al_a4'),
(12, 1, 'fed_i9', 'Federal I-9', 'employee_fed_i9s', 'fed_i9_id', 'hr/tax_forms/complete_fed_i9');"""
        )

        self.assertEquals([
            'Constraint error for foreign key `employee_contact_list_account_id_ref_accounts_id`: `employee_contract_list`.`account_id` references `accounts`.`id`, but table `accounts` does not exist'
        ], db.errors)
