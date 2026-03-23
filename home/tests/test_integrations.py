# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for soft integration endpoints (Tender, Orga).

These tests mock `frappe.get_installed_apps()` to simulate the
target app being present or absent.
"""

from unittest.mock import patch, MagicMock

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.integrations import (
	create_orga_project,
	create_tender_post,
	_map_category,
)


class TestTenderIntegration(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Tender Integration HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Tender Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
				"city": "Berlin",
			}
		).insert(ignore_permissions=True)

		task = frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Fix leaking pipe",
				"property": prop.name,
				"maintenance_type": "One-off",
				"category": "Plumbing",
				"status": "Scheduled",
				"notes": "Kitchen sink pipe dripping",
			}
		).insert(ignore_permissions=True)

		return hh, prop, task

	def test_throws_when_tender_not_installed(self):
		_hh, _prop, task = self._setup()

		with patch(
			"home.api.integrations.frappe.get_installed_apps",
			return_value=["frappe", "home"],
		):
			with self.assertRaises(frappe.ValidationError):
				create_tender_post(maintenance=task.name)

	def test_creates_tender_post(self):
		"""When Tender is installed, create_tender_post creates a post and links back."""
		_hh, _prop, task = self._setup()

		mock_post = MagicMock()
		mock_post.name = "TP-MOCK-001"

		with patch(
			"home.api.integrations.frappe.get_installed_apps",
			return_value=["frappe", "home", "tender"],
		), patch(
			"home.api.integrations.frappe.new_doc",
			return_value=mock_post,
		):
			result = create_tender_post(maintenance=task.name)

		self.assertEqual(result["tender_post"], "TP-MOCK-001")
		self.assertFalse(result["already_exists"])

		# Verify the post was populated correctly
		self.assertEqual(mock_post.title, "Fix leaking pipe")
		self.assertEqual(mock_post.description, "Kitchen sink pipe dripping")
		self.assertEqual(mock_post.category, "Plumbing")
		self.assertEqual(mock_post.location, "Berlin")
		self.assertEqual(mock_post.visibility, "Private")
		self.assertEqual(mock_post.source_app, "home")
		self.assertEqual(mock_post.source_doctype, "Home Maintenance")
		self.assertEqual(mock_post.source_name, task.name)
		mock_post.insert.assert_called_once()

	def test_idempotent_when_already_linked(self):
		"""If tender_post is already set, return it without creating a new one."""
		_hh, _prop, task = self._setup()

		# Simulate an existing link
		frappe.db.set_value("Home Maintenance", task.name, "tender_post", "TP-EXISTING")

		with patch(
			"home.api.integrations.frappe.get_installed_apps",
			return_value=["frappe", "home", "tender"],
		):
			result = create_tender_post(maintenance=task.name)

		self.assertEqual(result["tender_post"], "TP-EXISTING")
		self.assertTrue(result["already_exists"])

	def test_child_blocked(self):
		"""Child role cannot create a Tender post."""
		hh, _prop, task = self._setup()

		if not frappe.db.exists("User", "tenderchild@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "tenderchild@example.com",
					"first_name": "TenderChild",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh.append(
			"members",
			{"display_name": "Child", "role": "Child", "user": "tenderchild@example.com"},
		)
		hh.save(ignore_permissions=True)

		frappe.set_user("tenderchild@example.com")
		try:
			with patch(
				"home.api.integrations.frappe.get_installed_apps",
				return_value=["frappe", "home", "tender"],
			):
				self.assertRaises(
					frappe.PermissionError,
					create_tender_post,
					maintenance=task.name,
				)
		finally:
			frappe.set_user("Administrator")

	def test_category_mapping(self):
		"""_map_category maps Home categories to Tender categories."""
		self.assertEqual(_map_category("HVAC & Heating"), "Heating")
		self.assertEqual(_map_category("Plumbing"), "Plumbing")
		self.assertEqual(_map_category("Electrical"), "Electrical")
		self.assertEqual(_map_category("Roofing & Gutters"), "Roofing")
		self.assertEqual(_map_category("Carpentry"), "Carpentry")
		self.assertEqual(_map_category("Painting & Decorating"), "Decorating")
		self.assertEqual(_map_category("Cleaning"), "Cleaning")
		self.assertEqual(_map_category("Garden & Landscaping"), "Garden")
		self.assertEqual(_map_category("Pest Control"), "Pest Control")
		self.assertEqual(_map_category("Inspection"), "General")
		self.assertEqual(_map_category("General Repair"), "General")
		self.assertEqual(_map_category("Other"), "General")

	def test_category_mapping_unknown_defaults_to_general(self):
		self.assertEqual(_map_category("Something Unknown"), "General")
		self.assertEqual(_map_category(""), "General")
		self.assertEqual(_map_category(None), "General")

	def test_back_link_saved(self):
		"""After creation, tender_post is written back to the maintenance record."""
		_hh, _prop, task = self._setup()

		mock_post = MagicMock()
		mock_post.name = "TP-BACKLINK"

		with patch(
			"home.api.integrations.frappe.get_installed_apps",
			return_value=["frappe", "home", "tender"],
		), patch(
			"home.api.integrations.frappe.new_doc",
			return_value=mock_post,
		):
			create_tender_post(maintenance=task.name)

		saved_value = frappe.db.get_value("Home Maintenance", task.name, "tender_post")
		self.assertEqual(saved_value, "TP-BACKLINK")


class TestOrgaIntegration(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Orga Integration HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Orga Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
				"city": "Munich",
			}
		).insert(ignore_permissions=True)

		task = frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Kitchen renovation",
				"property": prop.name,
				"maintenance_type": "One-off",
				"category": "General Repair",
				"status": "Scheduled",
			}
		).insert(ignore_permissions=True)

		return hh, prop, task

	def test_throws_when_orga_not_installed(self):
		_hh, _prop, task = self._setup()

		with patch(
			"home.api.integrations.frappe.get_installed_apps",
			return_value=["frappe", "home"],
		):
			with self.assertRaises(frappe.ValidationError):
				create_orga_project(maintenance_name=task.name)
