# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeMaintenanceTemplate(FrappeTestCase):
	def _make_system_template(self):
		"""Create a system template (with install flag to bypass guard)."""
		frappe.flags.in_install = True
		try:
			doc = frappe.get_doc(
				{
					"doctype": "Home Maintenance Template",
					"template_name": "Test System Template",
					"season": "Annual",
					"is_system_template": 1,
					"tasks": [
						{"title": "Task A", "category": "Inspection", "days_offset": 0},
						{"title": "Task B", "category": "Plumbing", "days_offset": 3},
						{"title": "Task C", "category": "Electrical", "days_offset": 7},
					],
				}
			).insert(ignore_permissions=True)
		finally:
			frappe.flags.in_install = False
		return doc

	def _make_custom_template(self):
		"""Create a custom (user) template."""
		return frappe.get_doc(
			{
				"doctype": "Home Maintenance Template",
				"template_name": "My Custom Checklist",
				"season": "Custom",
				"is_system_template": 0,
				"tasks": [
					{"title": "Custom Task 1", "category": "Cleaning", "days_offset": 0},
					{"title": "Custom Task 2", "category": "Other", "days_offset": 5},
				],
			}
		).insert(ignore_permissions=True)

	def _setup_household(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Template Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Template Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_system_template_blocks_edit(self):
		tmpl = self._make_system_template()
		tmpl.template_name = "Modified Name"
		with self.assertRaises(frappe.ValidationError):
			tmpl.save()

	def test_system_template_blocks_delete(self):
		tmpl = self._make_system_template()
		with self.assertRaises(frappe.ValidationError):
			tmpl.delete()

	def test_custom_template_editable(self):
		tmpl = self._make_custom_template()
		tmpl.template_name = "Renamed Custom"
		tmpl.save()
		self.assertEqual(tmpl.template_name, "Renamed Custom")

	def test_custom_template_deletable(self):
		tmpl = self._make_custom_template()
		name = tmpl.name
		tmpl.delete()
		self.assertFalse(frappe.db.exists("Home Maintenance Template", name))


class TestMaintenanceTemplateAPI(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Template API HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Template API House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		frappe.flags.in_install = True
		try:
			tmpl = frappe.get_doc(
				{
					"doctype": "Home Maintenance Template",
					"template_name": "API Test Template",
					"season": "Winter",
					"is_system_template": 1,
					"tasks": [
						{"title": "Bleed radiators", "category": "HVAC & Heating", "days_offset": 0},
						{"title": "Insulate pipes", "category": "Plumbing", "days_offset": 3},
						{"title": "Seal drafts", "category": "General Repair", "days_offset": 7},
					],
				}
			).insert(ignore_permissions=True)
		finally:
			frappe.flags.in_install = False

		return hh, prop, tmpl

	def test_spawn_template(self):
		from home.api.maintenance import spawn_template

		_hh, prop, tmpl = self._setup()

		result = spawn_template(
			template=tmpl.name, property=prop.name, start_date="2026-11-15"
		)

		self.assertEqual(result["count"], 3)
		self.assertEqual(len(result["created"]), 3)

		# Check scheduled dates
		tasks = []
		for name in result["created"]:
			doc = frappe.get_doc("Home Maintenance", name)
			tasks.append(doc)

		titles = {t.title: str(t.scheduled_date) for t in tasks}
		self.assertEqual(titles["Bleed radiators"], "2026-11-15")
		self.assertEqual(titles["Insulate pipes"], "2026-11-18")
		self.assertEqual(titles["Seal drafts"], "2026-11-22")

		# All should be One-off and Scheduled
		for t in tasks:
			self.assertEqual(t.maintenance_type, "One-off")
			self.assertEqual(t.status, "Scheduled")

	def test_duplicate_template(self):
		from home.api.maintenance import duplicate_template

		_hh, _prop, tmpl = self._setup()

		result = duplicate_template(template=tmpl.name)
		copy = frappe.get_doc("Home Maintenance Template", result["name"])

		self.assertIn("Copy of", copy.template_name)
		self.assertEqual(copy.is_system_template, 0)
		self.assertEqual(len(copy.tasks), 3)

		# Copy should be editable
		copy.template_name = "My Winter Prep"
		copy.save()
		self.assertEqual(copy.template_name, "My Winter Prep")

	def test_get_template_preview(self):
		from home.api.maintenance import get_template_preview

		_hh, _prop, tmpl = self._setup()

		result = get_template_preview(template=tmpl.name, start_date="2026-11-01")

		self.assertEqual(result["template_name"], "API Test Template")
		self.assertEqual(len(result["tasks"]), 3)
		self.assertEqual(result["tasks"][0]["scheduled_date"], "2026-11-01")
		self.assertEqual(result["tasks"][1]["scheduled_date"], "2026-11-04")
		self.assertEqual(result["tasks"][2]["scheduled_date"], "2026-11-08")

	def test_get_templates(self):
		from home.api.maintenance import get_templates

		_hh, _prop, _tmpl = self._setup()

		result = get_templates()
		self.assertIn("system", result)
		self.assertIn("custom", result)

		system_names = [t["template_name"] for t in result["system"]]
		self.assertIn("API Test Template", system_names)

		# All system templates should have task_count
		for t in result["system"]:
			self.assertIn("task_count", t)
			self.assertGreater(t["task_count"], 0)
