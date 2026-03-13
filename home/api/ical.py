# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""iCal feed for maintenance schedules.

Per-property subscription via UUID token — no Frappe login required.
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_property_feed(token: str) -> str:
	"""Return iCal feed of scheduled maintenance for a property.

	Args:
		token: UUID ical_token from Home Property.

	Returns:
		iCalendar text/calendar response.
	"""
	if not token:
		frappe.throw(_("Token is required"), frappe.AuthenticationError)

	property_doc = frappe.db.get_value(
		"Home Property",
		{"ical_token": token},
		["name", "property_name"],
		as_dict=True,
	)

	if not property_doc:
		frappe.throw(_("Invalid or expired token"), frappe.AuthenticationError)

	tasks = frappe.get_all(
		"Home Maintenance",
		filters={
			"property": property_doc.name,
			"status": ["in", ["Scheduled", "In Progress"]],
			"scheduled_date": ["is", "set"],
		},
		fields=["name", "title", "scheduled_date", "category", "notes"],
	)

	lines = [
		"BEGIN:VCALENDAR",
		"VERSION:2.0",
		f"PRODID:-//Home//{property_doc.property_name}//EN",
		"CALSCALE:GREGORIAN",
		"METHOD:PUBLISH",
	]

	for task in tasks:
		date_str = frappe.utils.getdate(task.scheduled_date).strftime("%Y%m%d")
		lines.extend([
			"BEGIN:VEVENT",
			f"UID:{task.name}@home",
			f"DTSTART;VALUE=DATE:{date_str}",
			f"SUMMARY:{task.title}",
			f"DESCRIPTION:{task.category or ''}",
			"END:VEVENT",
		])

	lines.append("END:VCALENDAR")

	frappe.response["type"] = "text"
	frappe.response["content_type"] = "text/calendar; charset=utf-8"
	return "\r\n".join(lines)
