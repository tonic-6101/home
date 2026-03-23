# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeMortgage(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Mortgage Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Mortgage Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_household_fetched_from_property(self):
		hh, prop = self._setup()
		mortgage = frappe.get_doc(
			{
				"doctype": "Home Mortgage",
				"property": prop.name,
				"mortgage_name": "Primary Mortgage",
				"outstanding_balance": 250000,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(mortgage.household, hh.name)

	def test_equity_snapshot_on_balance_change(self):
		_hh, prop = self._setup()
		mortgage = frappe.get_doc(
			{
				"doctype": "Home Mortgage",
				"property": prop.name,
				"mortgage_name": "Primary Mortgage",
				"outstanding_balance": 250000,
			}
		).insert(ignore_permissions=True)

		# Change outstanding balance
		mortgage.outstanding_balance = 245000
		mortgage.save(ignore_permissions=True)

		# Reload property and check for equity snapshot
		prop.reload()
		self.assertTrue(
			len(prop.equity_snapshots) > 0,
			"Equity snapshot should be added to property when mortgage balance changes",
		)

	def test_archived_property_blocks_insert(self):
		_hh, prop = self._setup()
		prop.is_archived = 1
		prop.save(ignore_permissions=True)

		self.assertRaises(
			frappe.ValidationError,
			lambda: frappe.get_doc(
				{
					"doctype": "Home Mortgage",
					"property": prop.name,
					"mortgage_name": "Blocked Mortgage",
					"outstanding_balance": 100000,
				}
			).insert(ignore_permissions=True),
		)


class TestEquityAPI(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Equity API Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Equity Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
				"estimated_value": 200000,
				"estimated_value_date": "2026-01-15",
				"purchase_price": 150000,
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_get_equity_basic(self):
		from home.api.equity import get_equity

		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Mortgage",
				"property": prop.name,
				"mortgage_name": "Primary Mortgage",
				"outstanding_balance": 108000,
				"interest_rate": 2.35,
				"mortgage_type": "Repayment",
			}
		).insert(ignore_permissions=True)

		result = get_equity(property=prop.name)
		self.assertTrue(result["applicable"])
		self.assertEqual(result["estimated_value"], 200000)
		self.assertEqual(result["total_mortgage_balance"], 108000)
		self.assertEqual(result["equity_amount"], 92000)
		self.assertEqual(result["equity_pct"], 46.0)
		self.assertEqual(result["ltv"], 54.0)
		self.assertEqual(result["gain_vs_purchase"], 50000)
		self.assertAlmostEqual(result["gain_pct"], 33.3, places=1)
		self.assertEqual(len(result["mortgages"]), 1)

	def test_get_equity_multiple_mortgages(self):
		from home.api.equity import get_equity

		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Mortgage",
				"property": prop.name,
				"mortgage_name": "Primary",
				"outstanding_balance": 100000,
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Home Mortgage",
				"property": prop.name,
				"mortgage_name": "Secondary KfW",
				"outstanding_balance": 30000,
			}
		).insert(ignore_permissions=True)

		result = get_equity(property=prop.name)
		self.assertEqual(result["total_mortgage_balance"], 130000)
		self.assertEqual(result["equity_amount"], 70000)
		self.assertEqual(len(result["mortgages"]), 2)

	def test_get_equity_no_mortgage(self):
		from home.api.equity import get_equity

		hh, prop = self._setup()

		result = get_equity(property=prop.name)
		self.assertTrue(result["applicable"])
		self.assertEqual(result["total_mortgage_balance"], 0)
		self.assertEqual(result["equity_amount"], 200000)
		self.assertEqual(result["equity_pct"], 100.0)
		self.assertEqual(result["ltv"], 0.0)

	def test_get_equity_not_applicable_for_rented(self):
		from home.api.equity import get_equity

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Rented Equity HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Rented Place",
				"property_type": "Apartment",
				"ownership_status": "Rented",
			}
		).insert(ignore_permissions=True)

		result = get_equity(property=prop.name)
		self.assertFalse(result["applicable"])

	def test_get_equity_no_estimated_value(self):
		from home.api.equity import get_equity

		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "No Value Equity HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "No Value House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		result = get_equity(property=prop.name)
		self.assertFalse(result["has_estimated_value"])
		self.assertIsNone(result["equity_pct"])
		self.assertIsNone(result["ltv"])

	def test_update_value_records_snapshot(self):
		from home.api.equity import update_value

		hh, prop = self._setup()

		result = update_value(property=prop.name, estimated_value=220000, note="After renovation")
		self.assertEqual(result["estimated_value"], 220000)

		prop.reload()
		self.assertEqual(prop.estimated_value, 220000)
		self.assertTrue(len(prop.equity_snapshots) > 0)
		latest = prop.equity_snapshots[-1]
		self.assertEqual(latest.estimated_value, 220000)
		self.assertEqual(latest.note, "After renovation")

	def test_take_snapshot_manual(self):
		from home.api.equity import take_snapshot

		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Mortgage",
				"property": prop.name,
				"mortgage_name": "Primary",
				"outstanding_balance": 120000,
			}
		).insert(ignore_permissions=True)

		result = take_snapshot(property=prop.name, note="Year-end check")
		self.assertEqual(result["estimated_value"], 200000)
		self.assertEqual(result["total_mortgage_balance"], 120000)
		self.assertEqual(result["equity_amount"], 80000)
		self.assertEqual(result["note"], "Year-end check")

	def test_snapshot_pruning(self):
		from home.api.equity import take_snapshot

		hh, prop = self._setup()

		# Add 60 snapshots
		for i in range(60):
			prop.append("equity_snapshots", {
				"snapshot_date": f"2025-{(i % 12) + 1:02d}-01",
				"estimated_value": 200000,
				"total_mortgage_balance": 100000,
				"equity_amount": 100000,
				"equity_pct": 50.0,
			})
		prop.save(ignore_permissions=True)

		# Take one more — should trigger pruning
		take_snapshot(property=prop.name)
		prop.reload()
		self.assertLessEqual(len(prop.equity_snapshots), 60)

	def test_child_role_blocked(self):
		from home.api.equity import get_equity

		hh, prop = self._setup()

		if not frappe.db.exists("User", "eqchild@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "eqchild@example.com",
					"first_name": "EqChild",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh.append(
			"members",
			{"display_name": "Child", "role": "Child", "user": "eqchild@example.com"},
		)
		hh.save(ignore_permissions=True)

		frappe.set_user("eqchild@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				get_equity,
				property=prop.name,
			)
		finally:
			frappe.set_user("Administrator")

	def test_adult_can_view(self):
		from home.api.equity import get_equity

		hh, prop = self._setup()

		if not frappe.db.exists("User", "eqadult@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "eqadult@example.com",
					"first_name": "EqAdult",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh.append(
			"members",
			{"display_name": "Adult", "role": "Adult", "user": "eqadult@example.com"},
		)
		hh.save(ignore_permissions=True)

		frappe.set_user("eqadult@example.com")
		try:
			result = get_equity(property=prop.name)
			self.assertTrue(result["applicable"])
			self.assertEqual(result["estimated_value"], 200000)
		finally:
			frappe.set_user("Administrator")

	def test_negative_equity(self):
		from home.api.equity import get_equity

		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Mortgage",
				"property": prop.name,
				"mortgage_name": "Underwater Mortgage",
				"outstanding_balance": 250000,
			}
		).insert(ignore_permissions=True)

		result = get_equity(property=prop.name)
		self.assertEqual(result["equity_amount"], -50000)
		self.assertTrue(result["equity_pct"] < 0)
