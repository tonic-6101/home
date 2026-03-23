# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeBudget(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Budget Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Budget Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_household_fetched_from_property(self):
		hh, prop = self._setup()
		budget = frappe.get_doc(
			{
				"doctype": "Home Budget",
				"property": prop.name,
				"budget_year": 2025,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(budget.household, hh.name)

	def test_unique_property_year(self):
		_hh, prop = self._setup()
		frappe.get_doc(
			{
				"doctype": "Home Budget",
				"property": prop.name,
				"budget_year": 2025,
			}
		).insert(ignore_permissions=True)

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Home Budget",
					"property": prop.name,
					"budget_year": 2025,
				}
			).insert(ignore_permissions=True)


class TestBudgetOverviewAPI(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Budget API Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Budget API Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
				"purchase_price": 300000,
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_get_overview_creates_budget(self):
		from home.api.budget import get_overview

		_hh, prop = self._setup()
		result = get_overview(property=prop.name, year=2025)

		self.assertEqual(result["year"], 2025)
		self.assertIn("lines", result)
		self.assertIn("soft_lines", result)
		self.assertIn("totals", result)
		self.assertIn("pace", result)
		self.assertEqual(len(result["lines"]), 6)

	def test_get_overview_default_categories(self):
		from home.api.budget import get_overview

		_hh, prop = self._setup()
		result = get_overview(property=prop.name, year=2025)

		categories = [line["category"] for line in result["lines"]]
		self.assertIn("Maintenance & Repairs", categories)
		self.assertIn("Utilities", categories)
		self.assertIn("Insurance", categories)

	def test_save_and_retrieve_targets(self):
		from home.api.budget import get_overview, save_targets

		_hh, prop = self._setup()
		save_targets(
			property=prop.name,
			year=2025,
			targets={"Maintenance & Repairs": 3000, "Utilities": 2400},
		)

		result = get_overview(property=prop.name, year=2025)
		targets_by_cat = {l["category"]: l["annual_target"] for l in result["lines"]}
		self.assertEqual(targets_by_cat["Maintenance & Repairs"], 3000)
		self.assertEqual(targets_by_cat["Utilities"], 2400)

	def test_suggest_targets_1pct_rule(self):
		from home.api.budget import suggest_targets

		_hh, prop = self._setup()
		result = suggest_targets(property=prop.name, year=2025)

		maint = result["suggestions"]["Maintenance & Repairs"]
		self.assertEqual(maint["amount"], 3000)
		self.assertEqual(maint["basis"], "1% of property value")

	def test_actuals_from_maintenance(self):
		from home.api.budget import get_overview

		_hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"property": prop.name,
				"title": "Fix boiler",
				"category": "HVAC",
				"maintenance_type": "One-off",
				"status": "Completed",
				"completed_date": "2025-03-01",
				"cost": 500,
			}
		).insert(ignore_permissions=True)

		result = get_overview(property=prop.name, year=2025)
		maint_line = next(l for l in result["lines"] if l["category"] == "Maintenance & Repairs")
		self.assertEqual(maint_line["actual_spend"], 500)

	def test_actuals_from_utility_bills(self):
		from home.api.budget import get_overview

		_hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": "2025-01-01",
				"period_end": "2025-01-31",
				"amount": 120,
			}
		).insert(ignore_permissions=True)

		result = get_overview(property=prop.name, year=2025)
		util_line = next(l for l in result["lines"] if l["category"] == "Utilities")
		self.assertEqual(util_line["actual_spend"], 120)

	def test_soft_lines_empty_without_apps(self):
		"""Soft lines are empty when Rent/Mesa are not installed."""
		from home.api.budget import get_overview

		_hh, prop = self._setup()
		result = get_overview(property=prop.name, year=2025)

		# Rent and Mesa are not installed in test env
		self.assertEqual(result["soft_lines"], [])

	def test_rent_line_helper_not_installed(self):
		"""_get_rent_line returns empty when Rent is not installed."""
		from home.api.budget import _get_rent_line

		result = _get_rent_line(2025)
		self.assertEqual(result, [])

	def test_mesa_line_helper_not_installed(self):
		"""_get_mesa_line returns empty when Mesa is not installed."""
		from home.api.budget import _get_mesa_line

		result = _get_mesa_line(2025)
		self.assertEqual(result, [])

	def test_category_detail_maintenance(self):
		from home.api.budget import get_category_detail

		_hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"property": prop.name,
				"title": "Fix tap",
				"category": "Plumbing",
				"maintenance_type": "One-off",
				"status": "Completed",
				"completed_date": "2025-02-15",
				"cost": 80,
			}
		).insert(ignore_permissions=True)

		result = get_category_detail(property=prop.name, year=2025, category="Maintenance & Repairs")
		self.assertEqual(result["type"], "event")
		self.assertEqual(len(result["rows"]), 1)
		self.assertEqual(result["rows"][0]["cost"], 80)

	def test_child_blocked(self):
		from home.api.budget import get_overview

		hh, prop = self._setup()

		if not frappe.db.exists("User", "budgetchild@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "budgetchild@example.com",
					"first_name": "BudgetChild",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh_doc = frappe.get_doc("Home Household", hh.name)
		hh_doc.append(
			"members",
			{"display_name": "Child", "role": "Child", "user": "budgetchild@example.com"},
		)
		hh_doc.save(ignore_permissions=True)

		frappe.set_user("budgetchild@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				get_overview,
				property=prop.name,
				year=2025,
			)
		finally:
			frappe.set_user("Administrator")
