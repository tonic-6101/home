# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class TestHomeUtilityBill(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Utility Bill Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Utility Bill Test House",
				"property_type": "Apartment",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_household_fetched_from_property(self):
		hh, prop = self._setup()
		bill = frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": "2025-01-01",
				"period_end": "2025-01-31",
				"amount": 120,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(bill.household, hh.name)

	def test_consumption_computed(self):
		_hh, prop = self._setup()
		bill = frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": "2025-01-01",
				"period_end": "2025-01-31",
				"amount": 120,
				"reading_start": 100,
				"reading_end": 150,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(bill.consumption_amount, 50)

	def test_paid_date_auto_set(self):
		_hh, prop = self._setup()
		bill = frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": "2025-01-01",
				"period_end": "2025-01-31",
				"amount": 120,
			}
		).insert(ignore_permissions=True)

		bill.paid = 1
		bill.save(ignore_permissions=True)

		self.assertEqual(str(bill.paid_date), today())

	def test_direct_consumption_entry_preserved(self):
		"""Direct consumption_amount is preserved when no meter readings."""
		_hh, prop = self._setup()
		bill = frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Gas",
				"period_start": "2025-02-01",
				"period_end": "2025-02-28",
				"amount": 90,
				"consumption_amount": 320,
				"consumption_unit": "m³",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(bill.consumption_amount, 320)
		self.assertEqual(bill.consumption_unit, "m³")

	def test_meter_readings_override_direct_entry(self):
		"""Meter readings override direct consumption_amount entry."""
		_hh, prop = self._setup()
		bill = frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": "2025-03-01",
				"period_end": "2025-03-31",
				"amount": 100,
				"consumption_amount": 999,
				"reading_start": 200,
				"reading_end": 280,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(bill.consumption_amount, 80)

	def test_default_consumption_unit_electricity(self):
		"""Electricity defaults to kWh."""
		_hh, prop = self._setup()
		bill = frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": "2025-04-01",
				"period_end": "2025-04-30",
				"amount": 110,
				"reading_start": 500,
				"reading_end": 900,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(bill.consumption_unit, "kWh")

	def test_default_consumption_unit_water(self):
		"""Water defaults to m³."""
		_hh, prop = self._setup()
		bill = frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Water",
				"period_start": "2025-05-01",
				"period_end": "2025-05-31",
				"amount": 40,
				"consumption_amount": 12,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(bill.consumption_unit, "m³")

	def test_no_default_unit_for_internet(self):
		"""Internet has no consumption unit — stays None."""
		_hh, prop = self._setup()
		bill = frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Internet",
				"period_start": "2025-06-01",
				"period_end": "2025-06-30",
				"amount": 35,
				"consumption_amount": 100,
			}
		).insert(ignore_permissions=True)

		self.assertFalse(bill.consumption_unit)

	def test_archived_property_blocks_insert(self):
		_hh, prop = self._setup()
		prop.is_archived = 1
		prop.save(ignore_permissions=True)

		self.assertRaises(
			frappe.ValidationError,
			lambda: frappe.get_doc(
				{
					"doctype": "Home Utility Bill",
					"property": prop.name,
					"bill_type": "Electricity",
					"period_start": "2025-07-01",
					"period_end": "2025-07-31",
					"amount": 100,
				}
			).insert(ignore_permissions=True),
		)


class TestConsumptionTrendsAPI(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Consumption Trends HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Consumption Trends House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
				"area_sqm": 150,
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def _add_bill(self, prop_name, month, amount, consumption, unit="kWh", year=2025):
		return frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop_name,
				"bill_type": "Electricity",
				"period_start": f"{year}-{month:02d}-01",
				"period_end": f"{year}-{month:02d}-28",
				"amount": amount,
				"consumption_amount": consumption,
				"consumption_unit": unit,
			}
		).insert(ignore_permissions=True)

	def test_basic_consumption_trends(self):
		from home.api.utility import get_consumption_trends

		_hh, prop = self._setup()

		self._add_bill(prop.name, 1, 100, 400)
		self._add_bill(prop.name, 2, 110, 420)
		self._add_bill(prop.name, 3, 95, 380)

		result = get_consumption_trends(property=prop.name, year=2025, utility_type="Electricity")

		self.assertEqual(result["year"], 2025)
		self.assertEqual(result["utility_type"], "Electricity")
		self.assertEqual(result["unit"], "kWh")
		self.assertEqual(result["total_consumption"], 1200)
		self.assertEqual(result["total_cost"], 305)
		self.assertEqual(len(result["monthly"]), 12)
		self.assertEqual(result["monthly"][0]["consumption"], 400)
		self.assertEqual(result["monthly"][1]["consumption"], 420)
		self.assertEqual(result["monthly"][2]["consumption"], 380)
		self.assertEqual(result["monthly"][3]["consumption"], 0)

	def test_per_sqm_metric(self):
		from home.api.utility import get_consumption_trends

		_hh, prop = self._setup()

		self._add_bill(prop.name, 1, 100, 450)

		result = get_consumption_trends(property=prop.name, year=2025, utility_type="Electricity")

		# 450 kWh / 150 m² = 3.0
		self.assertEqual(result["per_sqm"], 3.0)

	def test_per_sqm_none_without_area(self):
		from home.api.utility import get_consumption_trends

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "No Area HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "No Area House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		self._add_bill(prop.name, 1, 100, 450)

		result = get_consumption_trends(property=prop.name, year=2025, utility_type="Electricity")
		self.assertIsNone(result["per_sqm"])

	def test_yoy_comparison(self):
		from home.api.utility import get_consumption_trends

		_hh, prop = self._setup()

		# Prior year
		self._add_bill(prop.name, 1, 100, 500, year=2024)
		self._add_bill(prop.name, 2, 100, 500, year=2024)

		# Current year — consumption down, cost up
		self._add_bill(prop.name, 1, 120, 450, year=2025)
		self._add_bill(prop.name, 2, 120, 460, year=2025)

		result = get_consumption_trends(property=prop.name, year=2025, utility_type="Electricity")

		self.assertEqual(result["prior_consumption"], 1000)
		self.assertEqual(result["prior_cost"], 200)
		self.assertEqual(result["total_consumption"], 910)
		self.assertEqual(result["total_cost"], 240)

		# Consumption dropped 9%
		self.assertAlmostEqual(result["consumption_change_pct"], -9.0, places=1)
		# Cost up 20%
		self.assertAlmostEqual(result["cost_change_pct"], 20.0, places=1)

	def test_no_prior_year_data(self):
		from home.api.utility import get_consumption_trends

		_hh, prop = self._setup()
		self._add_bill(prop.name, 1, 100, 400)

		result = get_consumption_trends(property=prop.name, year=2025, utility_type="Electricity")

		self.assertIsNone(result["consumption_change_pct"])
		self.assertIsNone(result["cost_change_pct"])
		self.assertEqual(result["prior_consumption"], 0)

	def test_bills_without_consumption_count(self):
		from home.api.utility import get_consumption_trends

		_hh, prop = self._setup()

		# One bill with consumption
		self._add_bill(prop.name, 1, 100, 400)

		# Two bills without consumption
		frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": "2025-02-01",
				"period_end": "2025-02-28",
				"amount": 110,
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": "2025-03-01",
				"period_end": "2025-03-31",
				"amount": 95,
			}
		).insert(ignore_permissions=True)

		result = get_consumption_trends(property=prop.name, year=2025, utility_type="Electricity")
		self.assertEqual(result["bills_without_consumption"], 2)

	def test_child_blocked(self):
		from home.api.utility import get_consumption_trends

		_hh, prop = self._setup()
		_hh = frappe.get_doc("Home Household", _hh.name)

		if not frappe.db.exists("User", "utilchild@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "utilchild@example.com",
					"first_name": "UtilChild",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		_hh.append(
			"members",
			{"display_name": "Child", "role": "Child", "user": "utilchild@example.com"},
		)
		_hh.save(ignore_permissions=True)

		frappe.set_user("utilchild@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				get_consumption_trends,
				property=prop.name,
				year=2025,
				utility_type="Electricity",
			)
		finally:
			frappe.set_user("Administrator")

	def test_empty_year(self):
		from home.api.utility import get_consumption_trends

		_hh, prop = self._setup()

		result = get_consumption_trends(property=prop.name, year=2025, utility_type="Electricity")

		self.assertEqual(result["total_consumption"], 0)
		self.assertIsNone(result["unit"])
		self.assertIsNone(result["per_sqm"])
		self.assertEqual(result["bills_without_consumption"], 0)
		self.assertEqual(len(result["monthly"]), 12)
		for entry in result["monthly"]:
			self.assertEqual(entry["consumption"], 0)
