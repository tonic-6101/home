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

	def _make_property(self, household, **kwargs):
		data = {
			"doctype": "Home Property",
			"household": household.name,
			"property_name": "Test House",
			"property_type": "House",
			"ownership_status": "Owner-occupied",
		}
		data.update(kwargs)
		return frappe.get_doc(data).insert(ignore_permissions=True)

	def test_create_property(self):
		hh = self._make_household()
		prop = self._make_property(hh)
		self.assertTrue(prop.name)
		self.assertEqual(prop.property_name, "Test House")
		self.assertEqual(prop.household, hh.name)

	def test_country_defaults_to_site_default(self):
		hh = self._make_household()
		prop = self._make_property(hh)
		site_country = frappe.db.get_default("country")
		if site_country:
			self.assertEqual(prop.country, site_country)

	def test_country_not_overwritten_when_set(self):
		hh = self._make_household()
		prop = self._make_property(hh, country="Germany")
		self.assertEqual(prop.country, "Germany")

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

	def test_archived_property_blocks_child_creation(self):
		hh = self._make_household()
		prop = self._make_property(hh)
		prop.is_archived = 1
		prop.save(ignore_permissions=True)

		self.assertRaises(
			frappe.ValidationError,
			frappe.get_doc(
				{
					"doctype": "Home Room",
					"property": prop.name,
					"household": hh.name,
					"room_name": "Kitchen",
					"room_type": "Kitchen",
				}
			).insert,
			ignore_permissions=True,
		)

	def test_non_owner_cannot_edit_property(self):
		hh = self._make_household()
		# Add an Adult member
		hh.append(
			"members",
			{
				"display_name": "Adult User",
				"role": "Adult",
				"user": "test@example.com",
			},
		)
		hh.save(ignore_permissions=True)

		prop = self._make_property(hh)

		# Simulate Adult user editing
		frappe.set_user("test@example.com")
		try:
			prop.reload()
			prop.property_name = "Renamed by Adult"
			self.assertRaises(frappe.PermissionError, prop.save)
		finally:
			frappe.set_user("Administrator")

	def test_owner_can_edit_property(self):
		hh = self._make_household()
		prop = self._make_property(hh)

		# Administrator is the Owner member — should be able to edit
		prop.property_name = "Renamed by Owner"
		prop.save(ignore_permissions=True)
		self.assertEqual(prop.property_name, "Renamed by Owner")

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


class TestPropertyAPI(FrappeTestCase):
	def test_create_property_auto_creates_household(self):
		from home.api.property import create_property

		result = create_property(
			property_name="API Test House",
			property_type="House",
			ownership_status="Owner-occupied",
		)
		self.assertTrue(result["name"])
		self.assertTrue(result["household"])

		# Verify household was created
		hh = frappe.get_doc("Home Household", result["household"])
		self.assertTrue(hh.household_name.endswith("'s Home"))

	def test_create_property_uses_existing_household(self):
		from home.api.property import create_property

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Existing HH",
				"members": [
					{
						"display_name": "Admin",
						"role": "Owner",
						"user": "Administrator",
					}
				],
			}
		).insert(ignore_permissions=True)

		result = create_property(
			property_name="Second House",
			property_type="Apartment",
			ownership_status="Rented",
			household=hh.name,
		)
		self.assertEqual(result["household"], hh.name)

	def test_archive_property(self):
		from home.api.property import archive_property

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Archive Test HH",
				"members": [
					{
						"display_name": "Admin",
						"role": "Owner",
						"user": "Administrator",
					}
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "To Archive",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		archive_property(prop.name)

		prop.reload()
		self.assertEqual(prop.is_archived, 1)
		self.assertIsNotNone(prop.archived_date)

	def test_unarchive_property(self):
		from home.api.property import archive_property, unarchive_property

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Unarchive Test HH",
				"members": [
					{
						"display_name": "Admin",
						"role": "Owner",
						"user": "Administrator",
					}
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "To Unarchive",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		archive_property(prop.name)
		unarchive_property(prop.name)

		prop.reload()
		self.assertEqual(prop.is_archived, 0)
		self.assertIsNone(prop.archived_date)

	def test_list_properties_excludes_archived_by_default(self):
		from home.api.property import list_properties

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "List Test HH",
				"members": [
					{
						"display_name": "Admin",
						"role": "Owner",
						"user": "Administrator",
					}
				],
			}
		).insert(ignore_permissions=True)

		prop1 = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Active Prop",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		prop2 = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Archived Prop",
				"property_type": "Apartment",
				"ownership_status": "Rented",
				"is_archived": 1,
			}
		).insert(ignore_permissions=True)

		result = list_properties(household=hh.name)
		names = [r["name"] for r in result]
		self.assertIn(prop1.name, names)
		self.assertNotIn(prop2.name, names)

	def test_list_properties_includes_archived_when_requested(self):
		from home.api.property import list_properties

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "List Archived Test HH",
				"members": [
					{
						"display_name": "Admin",
						"role": "Owner",
						"user": "Administrator",
					}
				],
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Archived Prop 2",
				"property_type": "Apartment",
				"ownership_status": "Rented",
				"is_archived": 1,
			}
		).insert(ignore_permissions=True)

		result = list_properties(household=hh.name, include_archived=True)
		self.assertTrue(any(r["is_archived"] for r in result))

	def test_get_property_returns_computed_stats(self):
		from home.api.property import get_property

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Stats Test HH",
				"members": [
					{
						"display_name": "Admin",
						"role": "Owner",
						"user": "Administrator",
					}
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Stats House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		result = get_property(prop.name)
		self.assertIn("appliance_count", result)
		self.assertIn("open_maintenance_count", result)
		self.assertIn("upcoming_warranty_expiry", result)
		self.assertIn("members", result)
		self.assertEqual(result["appliance_count"], 0)
		self.assertEqual(result["open_maintenance_count"], 0)
