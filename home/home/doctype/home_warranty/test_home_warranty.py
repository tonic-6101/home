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
				"doctype": "Home Item",
				"item_type": "Appliance",
				"item_name": "Warranty Test Appliance",
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
				"item": appliance.name,
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
					"item": appliance.name,
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
				"item": appliance.name,
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


class TestWarrantyAPI(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Warranty API HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Warranty API House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		appliance = frappe.get_doc(
			{
				"doctype": "Home Item",
				"item_type": "Appliance",
				"item_name": "API Test Washer",
				"property": prop.name,
				"category": "White Goods",
				"status": "Working",
			}
		).insert(ignore_permissions=True)

		return hh, prop, appliance

	def test_get_warranties_with_expiry_status(self):
		from frappe.utils import add_days, today

		from home.api.warranty import get_warranties

		_hh, _prop, appliance = self._setup()

		# Active warranty — expires far in the future
		frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"item": appliance.name,
				"warranty_type": "Manufacturer",
				"start_date": "2025-01-01",
				"end_date": add_days(today(), 200),
			}
		).insert(ignore_permissions=True)

		# Expiring soon warranty — expires within 90 days
		frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"item": appliance.name,
				"warranty_type": "Extended",
				"start_date": "2024-01-01",
				"end_date": add_days(today(), 30),
			}
		).insert(ignore_permissions=True)

		# Expired warranty
		frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"item": appliance.name,
				"warranty_type": "Insurance",
				"start_date": "2023-01-01",
				"end_date": add_days(today(), -10),
			}
		).insert(ignore_permissions=True)

		result = get_warranties(item=appliance.name)
		warranties = result["warranties"]

		self.assertEqual(len(warranties), 3)

		statuses = {w["warranty_type"]: w["expiry_status"] for w in warranties}
		self.assertEqual(statuses["Manufacturer"], "active")
		self.assertEqual(statuses["Extended"], "expiring_soon")
		self.assertEqual(statuses["Insurance"], "expired")

	def test_get_warranty_detail_includes_claims(self):
		from home.api.warranty import get_warranty

		_hh, _prop, appliance = self._setup()

		warranty = frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"item": appliance.name,
				"warranty_type": "Manufacturer",
				"start_date": "2025-01-01",
				"end_date": "2027-01-01",
				"claims": [
					{
						"claim_date": "2025-06-15",
						"description": "Motor failed",
						"outcome": "Accepted",
						"amount_reimbursed": 350,
					},
					{
						"claim_date": "2026-01-10",
						"description": "Door seal leak",
						"outcome": "Partial",
						"amount_reimbursed": 45,
					},
				],
			}
		).insert(ignore_permissions=True)

		result = get_warranty(name=warranty.name)

		self.assertEqual(result["warranty_type"], "Manufacturer")
		self.assertIn("expiry_status", result)
		self.assertIn("days_remaining", result)
		self.assertEqual(len(result["claims"]), 2)
		self.assertEqual(result["claims"][0]["amount_reimbursed"], 350)

	def test_get_property_warranties(self):
		from home.api.warranty import get_property_warranties

		_hh, prop, appliance = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"item": appliance.name,
				"warranty_type": "Manufacturer",
				"start_date": "2025-01-01",
				"end_date": "2027-06-01",
			}
		).insert(ignore_permissions=True)

		result = get_property_warranties(property=prop.name)
		warranties = result["warranties"]

		self.assertGreaterEqual(len(warranties), 1)
		self.assertEqual(warranties[0]["item_name"], "API Test Washer")
