# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeWarranty(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Warranty Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Warranty Test House",
				"property_type": "Apartment",
				"ownership_status": "Rented",
			}
		).insert(ignore_permissions=True)

		appliance = frappe.get_doc(
			{
				"doctype": "Home Appliance",
				"appliance_name": "Warranty Test Appliance",
				"property": prop.name,
				"category": "White Goods",
				"status": "Working",
			}
		).insert(ignore_permissions=True)

		return hh, prop, appliance

	def test_auto_fetches_property_and_household(self):
		hh, prop, appliance = self._setup()
		warranty = frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"appliance": appliance.name,
				"warranty_type": "Manufacturer",
				"start_date": "2025-01-01",
				"end_date": "2027-01-01",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(warranty.property, prop.name)
		self.assertEqual(warranty.household, hh.name)

	def test_validates_start_before_end(self):
		_hh, _prop, appliance = self._setup()
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Home Warranty",
					"appliance": appliance.name,
					"warranty_type": "Manufacturer",
					"start_date": "2027-01-01",
					"end_date": "2025-01-01",
				}
			).insert(ignore_permissions=True)

	def test_warranty_with_claims(self):
		_hh, _prop, appliance = self._setup()
		warranty = frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"appliance": appliance.name,
				"warranty_type": "Manufacturer",
				"start_date": "2025-01-01",
				"end_date": "2027-01-01",
				"claims": [
					{
						"claim_date": "2025-06-15",
						"description": "Compressor failed",
						"outcome": "Accepted",
						"amount_reimbursed": 200,
					}
				],
			}
		).insert(ignore_permissions=True)

		self.assertEqual(len(warranty.claims), 1)
		self.assertEqual(warranty.claims[0].outcome, "Accepted")
