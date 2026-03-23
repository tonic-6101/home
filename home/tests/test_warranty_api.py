# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for Features 8–10 — Warranty API (records, expiry status, claims)."""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from home.api.warranty import (
	_compute_expiry_status,
	add_claim,
	get_warranties,
	get_warranty,
	update_claim,
)


class TestComputeExpiryStatus(FrappeTestCase):
	def test_active(self):
		future = add_days(today(), 120)
		status, days = _compute_expiry_status(future)
		self.assertEqual(status, "active")
		self.assertEqual(days, 120)

	def test_expiring_soon(self):
		soon = add_days(today(), 45)
		status, days = _compute_expiry_status(soon)
		self.assertEqual(status, "expiring_soon")
		self.assertEqual(days, 45)

	def test_expiring_soon_boundary(self):
		boundary = add_days(today(), 90)
		status, days = _compute_expiry_status(boundary)
		self.assertEqual(status, "expiring_soon")
		self.assertEqual(days, 90)

	def test_expired(self):
		past = add_days(today(), -10)
		status, days = _compute_expiry_status(past)
		self.assertEqual(status, "expired")
		self.assertEqual(days, 0)

	def test_expired_today(self):
		status, days = _compute_expiry_status(today())
		self.assertEqual(status, "expiring_soon")
		self.assertEqual(days, 0)


class TestWarrantyAPI(FrappeTestCase):
	def _setup(self):
		"""Create test household, property, and appliance."""
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Warranty Test Household",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Warranty Test Property",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		appliance = frappe.get_doc(
			{
				"doctype": "Home Item",
				"item_type": "Appliance",
				"property": prop.name,
				"item_name": "Warranty Test Dishwasher",
				"category": "White Goods",
				"brand": "Bosch",
				"status": "Working",
			}
		).insert(ignore_permissions=True)

		return hh, prop, appliance

	def _create_warranty(self, item_name, **kwargs):
		defaults = {
			"doctype": "Home Warranty",
			"item": item_name,
			"warranty_type": "Manufacturer",
			"start_date": add_days(today(), -365),
			"end_date": add_days(today(), 365),
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults).insert(ignore_permissions=True)

	def test_get_warranties_returns_expiry_status(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		self._create_warranty(appliance.name, provider="Bosch")

		result = get_warranties(item=appliance.name)

		self.assertIn("warranties", result)
		self.assertEqual(len(result["warranties"]), 1)

		w = result["warranties"][0]
		self.assertEqual(w["expiry_status"], "active")
		self.assertGreater(w["days_remaining"], 0)
		self.assertEqual(w["provider"], "Bosch")
		self.assertEqual(w["claim_count"], 0)
		self.assertIsNone(w["last_claim_outcome"])

	def test_get_warranties_with_claims(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(appliance.name)
		add_claim(
			warranty=warranty.name,
			claim_date=today(),
			description="Drum bearing failed",
			outcome="Accepted",
			amount_reimbursed=120,
		)

		result = get_warranties(item=appliance.name)
		w = result["warranties"][0]

		self.assertEqual(w["claim_count"], 1)
		self.assertEqual(w["last_claim_outcome"], "Accepted")

	def test_get_warranty_detail_includes_claims(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(appliance.name)
		add_claim(
			warranty=warranty.name,
			claim_date=today(),
			description="Door seal cracked",
			outcome="Pending",
		)

		result = get_warranty(name=warranty.name)

		self.assertIn("claims", result)
		self.assertEqual(len(result["claims"]), 1)
		self.assertEqual(result["claims"][0]["description"], "Door seal cracked")
		self.assertEqual(result["claims"][0]["outcome"], "Pending")

	def test_get_warranty_child_role_hides_amounts(self):
		"""Child role should not see amount_reimbursed in claims."""
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		# Add a Child member
		if not frappe.db.exists("User", "warranty_child@test.local"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "warranty_child@test.local",
					"first_name": "Child",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh_doc = frappe.get_doc("Home Household", hh.name)
		hh_doc.append("members", {
			"display_name": "Kid",
			"role": "Child",
			"user": "warranty_child@test.local",
		})
		hh_doc.save(ignore_permissions=True)

		warranty = self._create_warranty(appliance.name)
		add_claim(
			warranty=warranty.name,
			claim_date=today(),
			description="Test claim",
			outcome="Accepted",
			amount_reimbursed=150,
		)

		frappe.set_user("warranty_child@test.local")
		result = get_warranty(name=warranty.name)

		for claim in result["claims"]:
			self.assertNotIn("amount_reimbursed", claim)

		frappe.set_user("Administrator")

	def test_add_claim(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(appliance.name)

		result = add_claim(
			warranty=warranty.name,
			claim_date=today(),
			description="Motor failure",
			outcome="Pending",
			amount_reimbursed=0,
			notes="Ref: CLM-001",
		)

		self.assertEqual(result["warranty"], warranty.name)
		self.assertIn("claim_idx", result)

		warranty.reload()
		self.assertEqual(len(warranty.claims), 1)
		self.assertEqual(warranty.claims[0].description, "Motor failure")
		self.assertEqual(warranty.claims[0].notes, "Ref: CLM-001")

	def test_add_multiple_claims(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(appliance.name)

		add_claim(
			warranty=warranty.name,
			claim_date=add_days(today(), -30),
			description="First issue",
			outcome="Accepted",
			amount_reimbursed=50,
		)
		add_claim(
			warranty=warranty.name,
			claim_date=today(),
			description="Second issue",
			outcome="Pending",
		)

		warranty.reload()
		self.assertEqual(len(warranty.claims), 2)

	def test_add_claim_invalid_outcome(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(appliance.name)

		with self.assertRaises(frappe.ValidationError):
			add_claim(
				warranty=warranty.name,
				claim_date=today(),
				description="Bad outcome",
				outcome="InvalidOutcome",
			)

	def test_update_claim(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(appliance.name)
		result = add_claim(
			warranty=warranty.name,
			claim_date=today(),
			description="Pending claim",
			outcome="Pending",
		)

		update_claim(
			warranty=warranty.name,
			claim_idx=result["claim_idx"],
			outcome="Accepted",
			amount_reimbursed=200,
			notes="Approved by Bosch",
		)

		warranty.reload()
		claim = warranty.claims[0]
		self.assertEqual(claim.outcome, "Accepted")
		self.assertEqual(claim.amount_reimbursed, 200)
		self.assertEqual(claim.notes, "Approved by Bosch")

	def test_update_claim_not_found(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(appliance.name)

		with self.assertRaises(frappe.ValidationError):
			update_claim(
				warranty=warranty.name,
				claim_idx=999,
				outcome="Accepted",
			)

	def test_expired_warranty_status(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(
			appliance.name,
			start_date=add_days(today(), -730),
			end_date=add_days(today(), -30),
		)

		result = get_warranties(item=appliance.name)
		w = result["warranties"][0]

		self.assertEqual(w["expiry_status"], "expired")
		self.assertEqual(w["days_remaining"], 0)

	def test_expiring_soon_warranty_status(self):
		hh, prop, appliance = self._setup()
		frappe.set_user("Administrator")

		warranty = self._create_warranty(
			appliance.name,
			start_date=add_days(today(), -365),
			end_date=add_days(today(), 30),
		)

		result = get_warranties(item=appliance.name)
		w = result["warranties"][0]

		self.assertEqual(w["expiry_status"], "expiring_soon")
		self.assertEqual(w["days_remaining"], 30)
