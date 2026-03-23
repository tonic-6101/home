# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for the property health score API."""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from home.api.health import get_health_score


class TestHealthScore(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Health Score Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Health Score Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_perfect_score(self):
		"""A property with emergency info and insurance should score 100."""
		hh, prop = self._setup()
		frappe.set_user("Administrator")

		# Add emergency shutoff info to avoid -5 deduction
		prop.gas_shutoff_location = "Basement meter cupboard"
		prop.water_shutoff_location = "Under kitchen sink"
		prop.save(ignore_permissions=True)

		# Add an insurance policy to avoid -5 deduction
		frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Health Score Test Policy",
				"policy_type": "Buildings",
				"provider": "Test Insurer",
				"start_date": "2025-01-01",
				"end_date": "2027-01-01",
			}
		).insert(ignore_permissions=True)

		result = get_health_score(prop.name)

		self.assertEqual(result["score"], 100)
		self.assertEqual(result["band"], "Excellent")

	def test_overdue_maintenance_deducts(self):
		"""A property with overdue maintenance should score below 100."""
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Overdue Maint Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Overdue Maint Test House",
				"property_type": "Apartment",
				"ownership_status": "Rented",
			}
		).insert(ignore_permissions=True)

		# Create a maintenance task that is 5 days overdue
		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Overdue Filter Change",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Scheduled",
				"scheduled_date": add_days(today(), -5),
			}
		).insert(ignore_permissions=True)

		frappe.set_user("Administrator")

		result = get_health_score(prop.name)

		self.assertLess(result["score"], 100)
