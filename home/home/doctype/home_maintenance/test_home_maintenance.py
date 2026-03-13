# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestHomeMaintenance(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Maint Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Maint Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_one_off_task(self):
		hh, prop = self._setup()
		task = frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Fix leaking tap",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Scheduled",
				"scheduled_date": today(),
			}
		).insert(ignore_permissions=True)

		self.assertEqual(task.household, hh.name)
		self.assertEqual(task.status, "Scheduled")

	def test_recurring_creates_next_on_complete(self):
		hh, prop = self._setup()
		task = frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Monthly boiler check",
				"property": prop.name,
				"maintenance_type": "Recurring",
				"recurrence": "Monthly",
				"status": "Scheduled",
				"scheduled_date": "2025-01-15",
			}
		).insert(ignore_permissions=True)

		# Complete the task
		task.status = "Completed"
		task.completed_date = "2025-01-20"
		task.save(ignore_permissions=True)

		# Check that next occurrence was created
		next_tasks = frappe.get_all(
			"Home Maintenance",
			filters={
				"title": "Monthly boiler check",
				"property": prop.name,
				"status": "Scheduled",
				"name": ["!=", task.name],
			},
			fields=["scheduled_date"],
		)
		self.assertTrue(len(next_tasks) > 0)
		self.assertEqual(str(next_tasks[0].scheduled_date), "2025-02-20")

	def test_one_off_does_not_create_next(self):
		_hh, prop = self._setup()
		task = frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "One-time fix",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Scheduled",
				"scheduled_date": today(),
			}
		).insert(ignore_permissions=True)

		initial_count = frappe.db.count("Home Maintenance", {"property": prop.name})

		task.status = "Completed"
		task.completed_date = today()
		task.save(ignore_permissions=True)

		final_count = frappe.db.count("Home Maintenance", {"property": prop.name})
		self.assertEqual(initial_count, final_count)
