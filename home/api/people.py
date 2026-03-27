# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Dock People hub context provider.

Called by Dock's ``dock_people_context`` hook to show Home-related
information on a Contact's detail page — maintenance tasks where the
contact is listed as the contractor, and properties they're associated with.
"""

import frappe
from frappe import _


def get_contact_context(contact_name: str) -> dict | None:
	"""Return Home context panel for a contact.

	Shows maintenance tasks (Orga Tasks with Home context) where the contact
	is the contractor, and any associated properties.

	Args:
		contact_name: Name of the Frappe Contact record.

	Returns:
		dict with title, icon, and content list — or None if no data.
	"""
	items = []

	# Maintenance tasks where this contact is the Home contractor
	tasks = frappe.get_all(
		"Orga Task",
		filters={
			"home_contractor": contact_name,
			"home_property": ["is", "set"],
		},
		fields=["name", "subject", "status", "home_property", "home_maintenance_category"],
		order_by="creation desc",
		limit=10,
	)

	for task in tasks:
		prop_name = frappe.db.get_value(
			"Home Property", task.home_property, "property_name"
		) or task.home_property
		items.append({
			"type": "task",
			"label": task.subject,
			"status": task.status,
			"property": prop_name,
			"category": task.home_maintenance_category or "",
			"name": task.name,
		})

	if not items:
		return None

	return {
		"title": _("Home Maintenance"),
		"icon": "home",
		"items": items,
	}
