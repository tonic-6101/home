# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeSettings(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Settings Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		return hh

	def test_auto_created_on_household_insert(self):
		"""Home Settings is auto-created when a household is created."""
		hh = self._setup()
		settings = frappe.get_all(
			"Home Settings",
			filters={"household": hh.name},
			fields=["name"],
		)
		self.assertEqual(len(settings), 1)

	def test_default_values_populated(self):
		"""Auto-created settings have correct defaults."""
		hh = self._setup()
		settings = frappe.get_doc("Home Settings", {"household": hh.name})

		self.assertEqual(settings.warranty_alert_days_1, 90)
		self.assertEqual(settings.warranty_alert_days_2, 30)
		self.assertEqual(settings.maintenance_reminder_days, 3)
		self.assertEqual(settings.refund_overdue_days, 14)
		self.assertEqual(settings.insurance_renewal_days, 60)
		self.assertEqual(settings.financial_visibility, "Owner and Adult")

	def test_default_lifespan_rows_seeded(self):
		"""Auto-created settings include 7 category lifespan defaults."""
		hh = self._setup()
		settings = frappe.get_doc("Home Settings", {"household": hh.name})

		self.assertEqual(len(settings.lifespan_defaults), 7)
		categories = {r.category for r in settings.lifespan_defaults}
		self.assertIn("White Goods", categories)
		self.assertIn("HVAC", categories)
		self.assertIn("Electronics", categories)

	def test_get_threshold_returns_value(self):
		from home.home.doctype.home_settings.home_settings import get_threshold

		hh = self._setup()
		self.assertEqual(get_threshold(hh.name, "warranty_alert_days_1"), 90)

	def test_get_threshold_fallback_no_settings(self):
		"""get_threshold returns system default when no settings record exists."""
		from home.home.doctype.home_settings.home_settings import get_threshold

		# Use a fake household name that has no settings
		result = get_threshold("NONEXISTENT-HH", "warranty_alert_days_1")
		self.assertEqual(result, 90)

	def test_can_see_financial_data_owner(self):
		from home.home.doctype.home_settings.home_settings import can_see_financial_data

		hh = self._setup()
		self.assertTrue(can_see_financial_data(hh.name, "Owner"))

	def test_can_see_financial_data_adult_default(self):
		"""Adult can see financial data with default 'Owner and Adult' setting."""
		from home.home.doctype.home_settings.home_settings import can_see_financial_data

		hh = self._setup()
		self.assertTrue(can_see_financial_data(hh.name, "Adult"))

	def test_can_see_financial_data_adult_owner_only(self):
		"""Adult cannot see financial data when set to 'Owner only'."""
		from home.home.doctype.home_settings.home_settings import can_see_financial_data

		hh = self._setup()
		settings = frappe.get_doc("Home Settings", {"household": hh.name})
		settings.financial_visibility = "Owner only"
		settings.save(ignore_permissions=True)

		self.assertFalse(can_see_financial_data(hh.name, "Adult"))

	def test_can_see_financial_data_child_always_false(self):
		from home.home.doctype.home_settings.home_settings import can_see_financial_data

		hh = self._setup()
		self.assertFalse(can_see_financial_data(hh.name, "Child"))

	def test_before_save_applies_defaults_for_blank_fields(self):
		"""Controller fills blank threshold fields with defaults on save."""
		hh = self._setup()
		settings = frappe.get_doc("Home Settings", {"household": hh.name})
		settings.warranty_alert_days_1 = 0
		settings.save(ignore_permissions=True)

		settings.reload()
		self.assertEqual(settings.warranty_alert_days_1, 90)


class TestSettingsAPI(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Settings API Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		return hh

	def test_get_settings(self):
		from home.api.settings import get_settings

		hh = self._setup()

		result = get_settings(household=hh.name)
		self.assertEqual(result["household"], hh.name)
		self.assertEqual(result["warranty_alert_days_1"], 90)
		self.assertIn("category_lifespans", result)
		self.assertEqual(len(result["category_lifespans"]), 7)

	def test_get_settings_lazy_creates(self):
		"""get_settings creates settings record if none exists."""
		from home.api.settings import get_settings

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Lazy Init HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		# Delete auto-created settings to test lazy init
		existing = frappe.get_all("Home Settings", filters={"household": hh.name}, pluck="name")
		for name in existing:
			frappe.delete_doc("Home Settings", name, ignore_permissions=True)

		result = get_settings(household=hh.name)
		self.assertEqual(result["household"], hh.name)
		self.assertEqual(result["warranty_alert_days_1"], 90)
		self.assertEqual(len(result["category_lifespans"]), 7)

	def test_save_settings_scalar_fields(self):
		from home.api.settings import save_settings

		hh = self._setup()

		result = save_settings(
			household=hh.name,
			warranty_alert_days_1=60,
			maintenance_reminder_days=5,
		)
		self.assertIn("warranty_alert_days_1", result["updated_fields"])
		self.assertIn("maintenance_reminder_days", result["updated_fields"])

		settings = frappe.get_doc("Home Settings", {"household": hh.name})
		self.assertEqual(settings.warranty_alert_days_1, 60)
		self.assertEqual(settings.maintenance_reminder_days, 5)

	def test_save_settings_category_lifespans(self):
		from home.api.settings import save_settings

		hh = self._setup()

		new_lifespans = [
			{"category": "White Goods", "lifespan_years": 15, "avg_replacement_cost": 800},
			{"category": "HVAC", "lifespan_years": 18, "avg_replacement_cost": 3000},
		]
		result = save_settings(
			household=hh.name,
			category_lifespans=new_lifespans,
		)
		self.assertIn("category_lifespans", result["updated_fields"])

		settings = frappe.get_doc("Home Settings", {"household": hh.name})
		self.assertEqual(len(settings.lifespan_defaults), 2)
		wg = [r for r in settings.lifespan_defaults if r.category == "White Goods"][0]
		self.assertEqual(wg.lifespan_years, 15)
		self.assertEqual(wg.avg_replacement_cost, 800)

	def test_save_settings_rejects_invalid_fields(self):
		from home.api.settings import save_settings

		hh = self._setup()

		self.assertRaises(
			frappe.ValidationError,
			save_settings,
			household=hh.name,
			fake_field="hacked",
		)

	def test_save_settings_financial_visibility(self):
		from home.api.settings import save_settings

		hh = self._setup()

		save_settings(household=hh.name, financial_visibility="Owner only")

		settings = frappe.get_doc("Home Settings", {"household": hh.name})
		self.assertEqual(settings.financial_visibility, "Owner only")

	def test_get_settings_owner_only(self):
		"""Non-owner cannot access settings."""
		from home.api.settings import get_settings

		hh = self._setup()

		if not frappe.db.exists("User", "setadult@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "setadult@example.com",
					"first_name": "SetAdult",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh_doc = frappe.get_doc("Home Household", hh.name)
		hh_doc.append(
			"members",
			{"display_name": "Adult", "role": "Adult", "user": "setadult@example.com"},
		)
		hh_doc.save(ignore_permissions=True)

		frappe.set_user("setadult@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				get_settings,
				household=hh.name,
			)
		finally:
			frappe.set_user("Administrator")

	def test_save_settings_owner_only(self):
		"""Non-owner cannot save settings."""
		from home.api.settings import save_settings

		hh = self._setup()

		if not frappe.db.exists("User", "setadult2@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "setadult2@example.com",
					"first_name": "SetAdult2",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh_doc = frappe.get_doc("Home Household", hh.name)
		hh_doc.append(
			"members",
			{"display_name": "Adult", "role": "Adult", "user": "setadult2@example.com"},
		)
		hh_doc.save(ignore_permissions=True)

		frappe.set_user("setadult2@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				save_settings,
				household=hh.name,
				warranty_alert_days_1=60,
			)
		finally:
			frappe.set_user("Administrator")

	def test_item_inherits_lifespan_from_settings(self):
		"""Appliance item auto-populates expected_lifespan_years from Home Settings."""
		hh = self._setup()
		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Lifespan Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		item = frappe.get_doc(
			{
				"doctype": "Home Item",
				"item_type": "Appliance",
				"property": prop.name,
				"item_name": "Test Fridge",
				"category": "White Goods",
				"status": "Working",
			}
		).insert(ignore_permissions=True)

		# White Goods default lifespan = 12 years
		self.assertEqual(item.expected_lifespan_years, 12)
