# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeProperty(FrappeTestCase):
	def _make_household(self):
		return frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Property Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

	def _make_property(self, household):
		return frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": household.name,
				"property_name": "Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

	def test_create_property(self):
		hh = self._make_household()
		prop = self._make_property(hh)
		self.assertTrue(prop.name)
		self.assertEqual(prop.property_name, "Test House")
		self.assertEqual(prop.household, hh.name)

	def test_archived_date_set_on_archive(self):
		hh = self._make_household()
		prop = self._make_property(hh)
		self.assertIsNone(prop.archived_date)

		prop.is_archived = 1
		prop.save(ignore_permissions=True)
		self.assertIsNotNone(prop.archived_date)

	def test_archived_date_cleared_on_unarchive(self):
		hh = self._make_household()
		prop = self._make_property(hh)
		prop.is_archived = 1
		prop.save(ignore_permissions=True)

		prop.is_archived = 0
		prop.save(ignore_permissions=True)
		self.assertIsNone(prop.archived_date)

	def test_equity_snapshots_pruned_to_60(self):
		hh = self._make_household()
		prop = self._make_property(hh)

		for i in range(65):
			prop.append(
				"equity_snapshots",
				{
					"snapshot_date": f"2025-01-{(i % 28) + 1:02d}",
					"estimated_value": 100000 + i,
					"total_mortgage_balance": 50000,
					"equity_amount": 50000 + i,
					"equity_pct": 50,
				},
			)
		prop.save(ignore_permissions=True)
		self.assertLessEqual(len(prop.equity_snapshots), 60)
