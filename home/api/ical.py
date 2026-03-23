# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""iCal feed for maintenance schedules.

Per-property subscription via UUID token — no Frappe login required.
Responds with ``text/calendar`` containing VEVENTs for scheduled and
in-progress maintenance tasks.
"""

import frappe
from frappe import _
from frappe.utils import add_days, getdate


@frappe.whitelist(allow_guest=True)
def get_property_feed(token: str) -> None:
	"""Return iCal feed of scheduled maintenance for a property.

	Args:
		token: UUID ``ical_token`` from Home Property.
	"""
	if not token:
		frappe.throw(_("Token is required"), frappe.AuthenticationError)

	prop = frappe.db.get_value(
		"Home Property",
		{"ical_token": token, "is_archived": 0},
		["name", "property_name"],
		as_dict=True,
	)

	if not prop:
		frappe.throw(_("Invalid or expired calendar link"), frappe.PermissionError)

	tasks = frappe.get_all(
		"Home Maintenance",
		filters={
			"property": prop.name,
			"status": ["in", ["Scheduled", "In Progress"]],
			"scheduled_date": ["is", "set"],
		},
		fields=["name", "title", "category", "scheduled_date", "status", "contractor"],
	)

	site = frappe.local.site

	lines = [
		"BEGIN:VCALENDAR",
		"VERSION:2.0",
		f"PRODID:-//Home//{site}//EN",
		f"X-WR-CALNAME:{_escape_ical(prop.property_name)} — Maintenance",
		"X-WR-CALDESC:Home maintenance schedule",
		"CALSCALE:GREGORIAN",
		"METHOD:PUBLISH",
	]

	for task in tasks:
		contractor_name = ""
		if task.get("contractor"):
			contractor_name = (
				frappe.db.get_value("Contact", task["contractor"], "full_name")
				or ""
			)

		dt = getdate(task["scheduled_date"])
		date_str = dt.strftime("%Y%m%d")
		next_day_str = getdate(add_days(dt, 1)).strftime("%Y%m%d")

		description = f"Category: {task['category'] or 'General'}"
		if contractor_name:
			description += f"\\nContractor: {contractor_name}"

		status = "CONFIRMED" if task["status"] == "Scheduled" else "IN-PROCESS"
		url = f"https://{site}/home/maintenance/{task['name']}"

		lines.extend([
			"BEGIN:VEVENT",
			f"UID:{task['name']}@{site}",
			f"SUMMARY:{_escape_ical(task['title'])} — {_escape_ical(prop.property_name)}",
			f"DTSTART;VALUE=DATE:{date_str}",
			f"DTEND;VALUE=DATE:{next_day_str}",
			f"DESCRIPTION:{description}",
			f"URL:{url}",
			f"STATUS:{status}",
			"END:VEVENT",
		])

	lines.append("END:VCALENDAR")
	ical_content = "\r\n".join(lines)

	prop_slug = frappe.scrub(prop.property_name)
	frappe.local.response["type"] = "download"
	frappe.local.response["filename"] = f"home-{prop_slug}.ics"
	frappe.local.response["filecontent"] = ical_content.encode("utf-8")
	frappe.local.response["content_type"] = "text/calendar; charset=utf-8"


def _escape_ical(text: str) -> str:
	"""Escape special characters for iCalendar text values."""
	if not text:
		return ""
	return (
		text.replace("\\", "\\\\")
		.replace(";", "\\;")
		.replace(",", "\\,")
		.replace("\n", "\\n")
	)
