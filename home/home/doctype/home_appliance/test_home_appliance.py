# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeAppliance(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Appliance Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Appliance Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_lifespan_auto_populated(self):
		hh, prop = self._setup()
		appliance = frappe.get_doc(
			{
				"doctype": "Home Appliance",
				"appliance_name": "Test Dishwasher",
				"property": prop.name,
				"category": "White Goods",
				"status": "Working",
			}
		).insert(ignore_permissions=True)

		# Should be populated from settings defaults (12 years for White Goods)
		self.assertEqual(appliance.expected_lifespan_years, 12)

	def test_household_fetched(self):
		hh, prop = self._setup()
		appliance = frappe.get_doc(
			{
				"doctype": "Home Appliance",
				"appliance_name": "Test Boiler",
				"property": prop.name,
				"category": "Heating",
				"status": "Working",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(appliance.household, hh.name)

	def test_custom_lifespan_not_overwritten(self):
		hh, prop = self._setup()
		appliance = frappe.get_doc(
			{
				"doctype": "Home Appliance",
				"appliance_name": "Custom Lifespan Appliance",
				"property": prop.name,
				"category": "White Goods",
				"status": "Working",
				"expected_lifespan_years": 5,
			}
		).insert(ignore_permissions=True)

		# Should keep the manually set value
		self.assertEqual(appliance.expected_lifespan_years, 5)
