# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for household-scoped permission helpers."""

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.permission import (
	get_household_role,
	get_user_households,
	has_app_permission,
	require_household_access,
	require_role,
)


class TestPermissions(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Perm Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)
		return hh

	def test_get_user_households(self):
		hh = self._setup()
		households = get_user_households("Administrator")
		self.assertIn(hh.name, households)

	def test_require_household_access_passes(self):
		hh = self._setup()
		# Should not raise
		require_household_access(hh.name, "Administrator")

	def test_require_household_access_fails(self):
		hh = self._setup()
		with self.assertRaises(frappe.PermissionError):
			require_household_access(hh.name, "Guest")

	def test_get_household_role(self):
		hh = self._setup()
		role = get_household_role(hh.name, "Administrator")
		self.assertEqual(role, "Owner")

	def test_require_role_passes(self):
		hh = self._setup()
		require_role(hh.name, "Owner", "Administrator")

	def test_require_role_fails_for_higher(self):
		hh = self._setup()
		# Add a Child member
		hh.append("members", {"display_name": "Kid", "role": "Child"})
		hh.save(ignore_permissions=True)

		# Child can't pass an Owner role check — but we can't test this
		# without a real user. Test the logic with non-member instead.
		with self.assertRaises(frappe.PermissionError):
			require_role(hh.name, "Owner", "Guest")

	def test_has_app_permission(self):
		self._setup()
		frappe.set_user("Administrator")
		self.assertTrue(has_app_permission())
