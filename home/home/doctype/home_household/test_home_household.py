# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeHousehold(FrappeTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")

	def _make_household(self, name="Test Household", user=None):
		user = user or "Administrator"
		doc = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": name,
				"members": [
					{"display_name": "Test Owner", "role": "Owner", "user": user},
				],
			}
		)
		doc.insert(ignore_permissions=True)
		return doc

	def test_create_household(self):
		household = self._make_household()
		self.assertTrue(household.name)
		self.assertEqual(household.household_name, "Test Household")
		self.assertEqual(len(household.members), 1)
		self.assertEqual(household.members[0].role, "Owner")

	def test_auto_creates_settings(self):
		household = self._make_household()
		settings = frappe.db.exists("Home Settings", {"household": household.name})
		self.assertTrue(settings)

		settings_doc = frappe.get_doc("Home Settings", settings)
		self.assertEqual(settings_doc.warranty_alert_days_1, 90)
		self.assertEqual(settings_doc.warranty_alert_days_2, 30)
		self.assertEqual(settings_doc.maintenance_reminder_days, 3)
		self.assertEqual(len(settings_doc.lifespan_defaults), 7)

	def test_requires_at_least_one_owner(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Home Household",
					"household_name": "No Owner Household",
					"members": [
						{"display_name": "Adult", "role": "Adult", "user": "Administrator"},
					],
				}
			).insert(ignore_permissions=True)

	def test_unique_users_in_members(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Home Household",
					"household_name": "Duplicate User Household",
					"members": [
						{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
						{"display_name": "Dupe", "role": "Adult", "user": "Administrator"},
					],
				}
			).insert(ignore_permissions=True)

	def test_user_permissions_synced(self):
		household = self._make_household()
		perms = frappe.get_all(
			"User Permission",
			filters={
				"allow": "Home Household",
				"for_value": household.name,
				"user": "Administrator",
			},
		)
		self.assertTrue(len(perms) > 0)
