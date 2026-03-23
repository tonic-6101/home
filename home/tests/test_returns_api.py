# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for Feature 18 — Purchase Returns API."""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from home.api.returns import (
	create_return,
	get_return,
	get_returns,
	mark_refund_received,
	update_return,
)


class TestReturnsAPI(FrappeTestCase):
	def _setup(self):
		"""Create test household, property, and appliance."""
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Returns Test Household",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Returns Test Property",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		appliance = frappe.get_doc(
			{
				"doctype": "Home Item",
				"item_type": "Appliance",
				"property": prop.name,
				"item_name": "Returns Test Dishwasher",
				"category": "White Goods",
				"brand": "Bosch",
				"status": "Working",
			}
		).insert(ignore_permissions=True)

		return hh, prop, appliance

	def _create_return(self, property_name, **kwargs):
		defaults = {
			"property": property_name,
			"item_description": "Test Item",
			"return_date": today(),
			"return_reason": "Defective",
		}
		defaults.update(kwargs)
		result = create_return(**defaults)
		return result["purchase_return"]

	def test_create_return(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		result = create_return(
			property=prop.name,
			item_description="Bosch Dishwasher WAT28461",
			return_date=today(),
			return_reason="Defective",
			retailer="MediaMarkt",
			refund_expected=480,
		)

		self.assertIn("purchase_return", result)

		doc = frappe.get_doc("Home Purchase Return", result["purchase_return"])
		self.assertEqual(doc.item_description, "Bosch Dishwasher WAT28461")
		self.assertEqual(doc.retailer, "MediaMarkt")
		self.assertEqual(doc.return_reason, "Defective")
		self.assertEqual(doc.refund_status, "Pending")
		self.assertEqual(doc.refund_expected, 480)
		self.assertEqual(doc.household, hh.name)

	def test_create_return_invalid_reason(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		with self.assertRaises(frappe.ValidationError):
			create_return(
				property=prop.name,
				item_description="Bad Reason Item",
				return_date=today(),
				return_reason="InvalidReason",
			)

	def test_create_return_invalid_status(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		with self.assertRaises(frappe.ValidationError):
			create_return(
				property=prop.name,
				item_description="Bad Status Item",
				return_date=today(),
				return_reason="Defective",
				refund_status="InvalidStatus",
			)

	def test_create_return_with_linked_item(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		result = create_return(
			property=prop.name,
			item_description=appliance.item_name,
			return_date=today(),
			return_reason="Defective",
			linked_item=appliance.name,
		)

		doc = frappe.get_doc("Home Purchase Return", result["purchase_return"])
		self.assertEqual(doc.linked_item, appliance.name)

	def test_get_returns(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		self._create_return(prop.name, item_description="Item A", retailer="Amazon")
		self._create_return(prop.name, item_description="Item B", retailer="MediaMarkt")

		result = get_returns(property=prop.name)

		self.assertIn("returns", result)
		self.assertEqual(len(result["returns"]), 2)

	def test_get_returns_overdue_flag(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		# Create a return from 20 days ago — should be overdue
		self._create_return(
			prop.name,
			item_description="Old Return",
			return_date=add_days(today(), -20),
		)
		# Create a return from today — not overdue
		self._create_return(
			prop.name,
			item_description="Fresh Return",
			return_date=today(),
		)

		result = get_returns(property=prop.name)
		returns_by_desc = {r["item_description"]: r for r in result["returns"]}

		self.assertTrue(returns_by_desc["Old Return"]["overdue_followup"])
		self.assertEqual(returns_by_desc["Old Return"]["days_since_return"], 20)
		self.assertFalse(returns_by_desc["Fresh Return"]["overdue_followup"])

	def test_get_return_detail(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		name = self._create_return(
			prop.name,
			item_description="Detail Test",
			retailer="IKEA",
			refund_expected=120,
		)

		result = get_return(name=name)
		self.assertEqual(result["item_description"], "Detail Test")
		self.assertEqual(result["retailer"], "IKEA")
		self.assertIn("days_since_return", result)
		self.assertIn("overdue_followup", result)

	def test_mark_refund_received_full(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		name = self._create_return(
			prop.name,
			item_description="Full Refund",
			refund_expected=200,
		)

		result = mark_refund_received(
			name=name,
			refund_amount_received=200,
		)

		self.assertEqual(result["refund_status"], "Received")

		doc = frappe.get_doc("Home Purchase Return", name)
		self.assertEqual(doc.refund_status, "Received")
		self.assertEqual(doc.refund_amount_received, 200)
		self.assertEqual(str(doc.refund_received_date), today())

	def test_mark_refund_received_partial(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		name = self._create_return(
			prop.name,
			item_description="Partial Refund",
			refund_expected=200,
		)

		result = mark_refund_received(
			name=name,
			refund_amount_received=80,
		)

		self.assertEqual(result["refund_status"], "Partially Received")

		doc = frappe.get_doc("Home Purchase Return", name)
		self.assertEqual(doc.refund_status, "Partially Received")
		self.assertEqual(doc.refund_amount_received, 80)

	def test_mark_refund_received_custom_date(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		name = self._create_return(prop.name, item_description="Custom Date")
		custom_date = add_days(today(), -3)

		mark_refund_received(
			name=name,
			refund_amount_received=50,
			refund_received_date=custom_date,
		)

		doc = frappe.get_doc("Home Purchase Return", name)
		self.assertEqual(str(doc.refund_received_date), custom_date)

	def test_update_return(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		name = self._create_return(prop.name, item_description="Update Test")

		update_return(
			name=name,
			retailer="Saturn",
			return_reason="Wrong Item",
			refund_expected=300,
		)

		doc = frappe.get_doc("Home Purchase Return", name)
		self.assertEqual(doc.retailer, "Saturn")
		self.assertEqual(doc.return_reason, "Wrong Item")
		self.assertEqual(doc.refund_expected, 300)

	def test_update_return_invalid_reason(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		name = self._create_return(prop.name, item_description="Bad Update")

		with self.assertRaises(frappe.ValidationError):
			update_return(name=name, return_reason="BadValue")

	def test_update_return_invalid_status(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		name = self._create_return(prop.name, item_description="Bad Status Update")

		with self.assertRaises(frappe.ValidationError):
			update_return(name=name, refund_status="BadStatus")

	def test_child_role_cannot_access(self):
		"""Child role should not see purchase returns at all."""
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		self._create_return(prop.name, item_description="Hidden from child")

		# Add a Child member
		if not frappe.db.exists("User", "returns_child@test.local"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "returns_child@test.local",
					"first_name": "Child",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh_doc = frappe.get_doc("Home Household", hh.name)
		hh_doc.append("members", {
			"display_name": "Kid",
			"role": "Child",
			"user": "returns_child@test.local",
		})
		hh_doc.save(ignore_permissions=True)

		frappe.set_user("returns_child@test.local")

		with self.assertRaises(frappe.PermissionError):
			get_returns(property=prop.name)

		frappe.set_user("Administrator")

	def test_household_auto_fetched(self):
		"""Household should be auto-fetched from property on save."""
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		name = self._create_return(prop.name, item_description="Auto Household")
		doc = frappe.get_doc("Home Purchase Return", name)
		self.assertEqual(doc.household, hh.name)
