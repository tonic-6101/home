# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeImprovementWish(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Improvement Wish Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Improvement Wish Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_household_fetched_from_property(self):
		hh, prop = self._setup()
		wish = frappe.get_doc(
			{
				"doctype": "Home Improvement Wish",
				"property": prop.name,
				"title": "New kitchen backsplash",
				"category": "Cosmetic",
				"priority": "Important",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(wish.household, hh.name)

	def test_default_status_wishlist(self):
		_hh, prop = self._setup()
		wish = frappe.get_doc(
			{
				"doctype": "Home Improvement Wish",
				"property": prop.name,
				"title": "Garden landscaping",
				"category": "Garden",
				"priority": "Nice to have",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(wish.status, "Wishlist")
