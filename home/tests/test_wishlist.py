# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for the wishlist API: converting wishes to maintenance tasks."""

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.wishlist import convert_to_maintenance


class TestWishlist(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Wishlist Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Wishlist Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_convert_to_maintenance(self):
		"""Converting a wish should create a Home Maintenance and link it back."""
		hh, prop = self._setup()
		frappe.set_user("Administrator")

		wish = frappe.get_doc(
			{
				"doctype": "Home Improvement Wish",
				"property": prop.name,
				"title": "Replace kitchen backsplash",
				"category": "Cosmetic",
				"priority": "Important",
				"status": "Wishlist",
			}
		).insert(ignore_permissions=True)

		result = convert_to_maintenance(wish.name)

		# Reload the wish to check the link
		wish.reload()

		self.assertTrue(wish.linked_maintenance)
		self.assertTrue(frappe.db.exists("Home Maintenance", wish.linked_maintenance))

		# Verify the maintenance task has the correct title
		maint = frappe.get_doc("Home Maintenance", wish.linked_maintenance)
		self.assertEqual(maint.title, "Replace kitchen backsplash")
		self.assertEqual(maint.property, prop.name)
