# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeInsurancePolicy(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Insurance Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Insurance Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_household_fetched_from_property(self):
		hh, prop = self._setup()
		policy = frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Home Contents Insurance",
				"policy_type": "Contents",
				"provider": "Allianz",
				"start_date": "2025-01-01",
				"end_date": "2026-01-01",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(policy.household, hh.name)

	def test_renewal_notice_days_default(self):
		_hh, prop = self._setup()
		policy = frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Building Insurance",
				"policy_type": "Buildings",
				"provider": "AXA",
				"start_date": "2025-01-01",
				"end_date": "2026-01-01",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(policy.renewal_notice_days, 60)

	def test_validates_dates(self):
		_hh, prop = self._setup()
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Home Insurance Policy",
					"property": prop.name,
					"policy_name": "Bad Dates Policy",
					"policy_type": "Contents",
					"provider": "Test Insurer",
					"start_date": "2026-01-01",
					"end_date": "2025-01-01",
				}
			).insert(ignore_permissions=True)

	def test_archived_property_blocks_insert(self):
		_hh, prop = self._setup()
		prop.is_archived = 1
		prop.save(ignore_permissions=True)

		self.assertRaises(
			frappe.ValidationError,
			lambda: frappe.get_doc(
				{
					"doctype": "Home Insurance Policy",
					"property": prop.name,
					"policy_name": "Blocked Policy",
					"policy_type": "Contents",
					"provider": "Test",
					"start_date": "2025-01-01",
					"end_date": "2026-01-01",
				}
			).insert(ignore_permissions=True),
		)

	def test_claims_child_table(self):
		_hh, prop = self._setup()
		policy = frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Claims Test Policy",
				"policy_type": "Contents",
				"provider": "AXA",
				"start_date": "2025-01-01",
				"end_date": "2026-01-01",
				"claims": [
					{
						"claim_date": "2025-06-01",
						"incident_description": "Storm damage",
						"claim_amount": 1500,
						"outcome": "Approved",
						"payout_amount": 1350,
					},
					{
						"claim_date": "2025-09-15",
						"incident_description": "Theft",
						"claim_amount": 800,
						"outcome": "Pending",
					},
				],
			}
		).insert(ignore_permissions=True)

		self.assertEqual(len(policy.claims), 2)
		self.assertEqual(policy.claims[0].outcome, "Approved")
		self.assertEqual(policy.claims[1].outcome, "Pending")


class TestInsuranceAPI(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Ins API Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Ins API House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_get_policies_returns_list(self):
		from home.api.insurance import get_policies

		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Buildings Insurance",
				"policy_type": "Buildings",
				"provider": "AXA",
				"start_date": "2025-01-01",
				"end_date": "2027-01-01",
				"premium_annual": 600,
				"coverage_amount": 300000,
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Contents Insurance",
				"policy_type": "Contents",
				"provider": "Allianz",
				"start_date": "2025-04-01",
				"end_date": "2026-04-01",
				"premium_annual": 340,
				"coverage_amount": 35000,
			}
		).insert(ignore_permissions=True)

		result = get_policies(property=prop.name)
		self.assertEqual(len(result["policies"]), 2)
		self.assertEqual(result["total_annual_premium"], 940)

	def test_renewal_status_active(self):
		from frappe.utils import add_days, today
		from home.api.insurance import get_policies

		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Far Future Policy",
				"policy_type": "Buildings",
				"provider": "Test",
				"start_date": "2025-01-01",
				"end_date": add_days(today(), 200),
				"renewal_notice_days": 60,
			}
		).insert(ignore_permissions=True)

		result = get_policies(property=prop.name)
		self.assertEqual(result["policies"][0]["renewal_status"], "active")

	def test_renewal_status_renewing_soon(self):
		from frappe.utils import add_days, today
		from home.api.insurance import get_policies

		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Soon Policy",
				"policy_type": "Contents",
				"provider": "Test",
				"start_date": "2025-01-01",
				"end_date": add_days(today(), 30),
				"renewal_notice_days": 60,
			}
		).insert(ignore_permissions=True)

		result = get_policies(property=prop.name)
		self.assertEqual(result["policies"][0]["renewal_status"], "renewing_soon")

	def test_renewal_status_expired(self):
		from frappe.utils import add_days, today
		from home.api.insurance import get_policies

		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Old Policy",
				"policy_type": "Liability",
				"provider": "Test",
				"start_date": "2024-01-01",
				"end_date": add_days(today(), -10),
			}
		).insert(ignore_permissions=True)

		result = get_policies(property=prop.name)
		self.assertEqual(result["policies"][0]["renewal_status"], "expired")
		self.assertEqual(result["policies"][0]["days_to_renewal"], 0)

	def test_get_policy_detail_with_claims(self):
		from home.api.insurance import get_policy

		hh, prop = self._setup()

		policy = frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Detail Test Policy",
				"policy_type": "Contents",
				"provider": "Allianz",
				"start_date": "2025-01-01",
				"end_date": "2027-01-01",
				"premium_annual": 400,
				"coverage_amount": 50000,
				"auto_renews": 1,
				"claims": [
					{
						"claim_date": "2025-06-01",
						"incident_description": "Water damage",
						"claim_amount": 2000,
						"outcome": "Approved",
						"payout_amount": 1800,
					},
				],
			}
		).insert(ignore_permissions=True)

		result = get_policy(name=policy.name)
		self.assertEqual(result["policy_name"], "Detail Test Policy")
		self.assertEqual(result["premium_annual"], 400)
		self.assertEqual(result["auto_renews"], 1)
		self.assertIn("renewal_status", result)
		self.assertEqual(len(result["claims"]), 1)
		self.assertEqual(result["claims"][0].outcome, "Approved")

	def test_child_role_blocked_list(self):
		from home.api.insurance import get_policies

		hh, prop = self._setup()

		if not frappe.db.exists("User", "inschild@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "inschild@example.com",
					"first_name": "InsChild",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh.append(
			"members",
			{"display_name": "Child", "role": "Child", "user": "inschild@example.com"},
		)
		hh.save(ignore_permissions=True)

		frappe.set_user("inschild@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				get_policies,
				property=prop.name,
			)
		finally:
			frappe.set_user("Administrator")

	def test_child_role_blocked_detail(self):
		from home.api.insurance import get_policy

		hh, prop = self._setup()

		policy = frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Child Block Test",
				"policy_type": "Buildings",
				"provider": "Test",
				"start_date": "2025-01-01",
				"end_date": "2027-01-01",
			}
		).insert(ignore_permissions=True)

		if not frappe.db.exists("User", "inschild2@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "inschild2@example.com",
					"first_name": "InsChild2",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh.append(
			"members",
			{"display_name": "Child2", "role": "Child", "user": "inschild2@example.com"},
		)
		hh.save(ignore_permissions=True)

		frappe.set_user("inschild2@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				get_policy,
				name=policy.name,
			)
		finally:
			frappe.set_user("Administrator")
