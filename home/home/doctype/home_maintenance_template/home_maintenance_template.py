# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days


class HomeMaintenanceTemplate(Document):
	def validate(self):
		if self.is_system_template and not frappe.flags.in_install:
			frappe.throw(_("System templates cannot be edited"))


@frappe.whitelist()
def apply_template(template_name: str, property_name: str, start_date: str) -> list[str]:
	"""Spawn Home Maintenance tasks from a template for a given property.

	Args:
		template_name: Name of the Home Maintenance Template.
		property_name: Name of the Home Property to create tasks for.
		start_date: ISO date — tasks are scheduled relative to this date.

	Returns:
		List of created Home Maintenance names.
	"""
	template = frappe.get_doc("Home Maintenance Template", template_name)
	property_doc = frappe.get_doc("Home Property", property_name)

	created = []
	for task_row in template.tasks:
		scheduled = add_days(start_date, task_row.days_offset or 0)

		maintenance = frappe.new_doc("Home Maintenance")
		maintenance.title = task_row.title
		maintenance.property = property_doc.name
		maintenance.household = property_doc.household
		maintenance.maintenance_type = "One-off"
		maintenance.category = task_row.category
		maintenance.status = "Scheduled"
		maintenance.scheduled_date = scheduled
		maintenance.notes = task_row.notes
		maintenance.insert(ignore_permissions=True)
		created.append(maintenance.name)

	frappe.db.commit()
	return created
