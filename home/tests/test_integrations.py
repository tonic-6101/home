# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for soft integration endpoints (Tender, Orga).

These tests mock `frappe.get_installed_apps()` to simulate the
target app being present or absent.
"""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.integrations import create_orga_project, create_tender_post


class TestSoftIntegrations(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Integration Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Integration Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
				"city": "Berlin",
			}
		).insert(ignore_permissions=True)

		task = frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Integration Test Task",
				"property": prop.name,
				"maintenance_type": "One-off",
				"category": "Plumbing",
				"status": "Scheduled",
			}
		).insert(ignore_permissions=True)

		return hh, prop, task

	def test_tender_throws_when_not_installed(self):
		_hh, _prop, task = self._setup()

		with patch("home.api.integrations.frappe.get_installed_apps", return_value=["frappe", "home"]):
			with self.assertRaises(frappe.ValidationError):
				create_tender_post(task.name)

	def test_orga_throws_when_not_installed(self):
		_hh, _prop, task = self._setup()

		with patch("home.api.integrations.frappe.get_installed_apps", return_value=["frappe", "home"]):
			with self.assertRaises(frappe.ValidationError):
				create_orga_project(task.name)
