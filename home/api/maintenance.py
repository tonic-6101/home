# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Maintenance task APIs (Features 11 + 12).

Endpoints for listing maintenance tasks grouped by status,
completing tasks (with auto-recurrence), category-to-trade mapping,
and maintenance template spawn/duplicate.
"""

import frappe
from frappe import _
from frappe.utils import add_days, getdate, today

from home.api.permission import (
	get_household_role,
	require_household_access,
	require_role,
)


@frappe.whitelist()
def get_maintenance_list(property: str) -> dict:
	"""Return all maintenance tasks for a property, grouped by status.

	Groups: overdue, today, scheduled, in_progress, completed, cancelled.
	Overdue = status is Scheduled AND scheduled_date < today.
	Today = status is Scheduled AND scheduled_date == today.
	Cost field stripped for Child role.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	role = get_household_role(doc.household)

	all_tasks = frappe.get_all(
		"Home Maintenance",
		filters={"property": property},
		fields=[
			"name",
			"title",
			"category",
			"status",
			"maintenance_type",
			"recurrence",
			"scheduled_date",
			"completed_date",
			"room",
			"item",
			"contractor",
			"cost",
		],
		order_by="scheduled_date asc",
	)

	_today = frappe.utils.getdate(today())
	for t in all_tasks:
		sched = frappe.utils.getdate(t["scheduled_date"]) if t["scheduled_date"] else None
		t["overdue"] = (
			t["status"] == "Scheduled" and sched is not None and sched < _today
		)
		t["is_today"] = (
			t["status"] == "Scheduled" and sched is not None and sched == _today
		)
		if role == "Child":
			t.pop("cost", None)

	# Group by status
	overdue = sorted(
		[t for t in all_tasks if t["overdue"]],
		key=lambda t: t["scheduled_date"] or "",
	)
	due_today = sorted(
		[t for t in all_tasks if t["is_today"]],
		key=lambda t: t["title"] or "",
	)
	scheduled = sorted(
		[t for t in all_tasks if t["status"] == "Scheduled" and not t["overdue"] and not t["is_today"]],
		key=lambda t: t["scheduled_date"] or "",
	)
	in_progress = sorted(
		[t for t in all_tasks if t["status"] == "In Progress"],
		key=lambda t: t["scheduled_date"] or "",
	)
	completed = sorted(
		[t for t in all_tasks if t["status"] == "Completed"],
		key=lambda t: t["completed_date"] or "",
		reverse=True,
	)
	cancelled = [t for t in all_tasks if t["status"] == "Cancelled"]

	return {
		"overdue": overdue,
		"today": due_today,
		"scheduled": scheduled,
		"in_progress": in_progress,
		"completed": completed,
		"cancelled": cancelled,
	}


@frappe.whitelist()
def get_task(name: str) -> dict:
	"""Return a single maintenance task with resolved names.

	Resolves contractor_name, property_name, room_name, item_name.
	Includes soft integration fields (orga_project, tender_post) and
	flags for installed apps. Cost stripped for Child role.
	"""
	doc = frappe.get_doc("Home Maintenance", name)
	require_household_access(doc.household)
	role = get_household_role(doc.household)

	_today = getdate(today())
	sched = getdate(doc.scheduled_date) if doc.scheduled_date else None
	overdue = doc.status == "Scheduled" and sched is not None and sched < _today
	is_today = doc.status == "Scheduled" and sched is not None and sched == _today

	data = {
		"name": doc.name,
		"title": doc.title,
		"category": doc.category,
		"status": doc.status,
		"maintenance_type": doc.maintenance_type,
		"recurrence": doc.recurrence,
		"scheduled_date": str(doc.scheduled_date) if doc.scheduled_date else None,
		"completed_date": str(doc.completed_date) if doc.completed_date else None,
		"contractor": doc.contractor,
		"contractor_name": None,
		"property": doc.property,
		"property_name": frappe.db.get_value("Home Property", doc.property, "property_name"),
		"room": doc.room,
		"room_name": frappe.db.get_value("Home Room", doc.room, "room_name") if doc.room else None,
		"item": doc.item,
		"item_name": frappe.db.get_value(
			"Home Item", doc.item, "item_name"
		) if doc.item else None,
		"notes": doc.notes,
		"overdue": overdue,
		"is_today": is_today,
		"orga_project": doc.get("orga_project"),
		"tender_post": doc.get("tender_post"),
		"has_orga": "orga" in frappe.get_installed_apps(),
		"has_tender": "tender" in frappe.get_installed_apps(),
	}

	if doc.contractor:
		data["contractor_name"] = frappe.db.get_value(
			"Contact", doc.contractor, "full_name"
		)

	if role != "Child":
		data["cost"] = doc.cost

	return data


@frappe.whitelist()
def complete_task(
	name: str,
	completed_date: str | None = None,
	cost: float | None = None,
	notes: str | None = None,
) -> dict:
	"""Mark a maintenance task as completed.

	Collects completed_date (defaults to today), optional cost and notes.
	Triggers auto-creation of next occurrence for recurring tasks via
	the DocType controller's on_update hook.

	Returns:
		dict with success flag and next_occurrence name (if created).
	"""
	doc = frappe.get_doc("Home Maintenance", name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	doc.status = "Completed"
	doc.completed_date = completed_date or today()
	if cost is not None:
		doc.cost = cost
	if notes:
		doc.notes = notes
	doc.save()

	return {
		"ok": True,
		"next_occurrence": _get_next_occurrence(doc),
	}


def _get_next_occurrence(doc) -> str | None:
	"""Return the name of the auto-created next occurrence, if any."""
	if doc.maintenance_type != "Recurring":
		return None

	return frappe.db.get_value(
		"Home Maintenance",
		{
			"title": doc.title,
			"property": doc.property,
			"status": "Scheduled",
			"name": ["!=", doc.name],
		},
		"name",
		order_by="creation desc",
	)


# ---------------------------------------------------------------------------
# Feature 12 — Maintenance Templates
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_templates() -> dict:
	"""Return all maintenance templates grouped by system vs custom.

	Returns:
		dict with "system" and "custom" lists.
	"""
	templates = frappe.get_all(
		"Home Maintenance Template",
		fields=[
			"name",
			"template_name",
			"season",
			"is_system_template",
			"description",
		],
		order_by="is_system_template desc, template_name asc",
	)

	for t in templates:
		t["task_count"] = frappe.db.count(
			"Home Maintenance Template Task", {"parent": t["name"]}
		)

	system = [t for t in templates if t["is_system_template"]]
	custom = [t for t in templates if not t["is_system_template"]]

	return {"system": system, "custom": custom}


@frappe.whitelist()
def get_template_preview(template: str, start_date: str) -> dict:
	"""Preview tasks that would be created from a template.

	Args:
		template: Name of the Home Maintenance Template.
		start_date: ISO date string for scheduling.

	Returns:
		dict with template_name and tasks list.
	"""
	tmpl = frappe.get_doc("Home Maintenance Template", template)
	start = getdate(start_date)

	tasks = []
	for row in tmpl.tasks:
		tasks.append(
			{
				"title": row.title,
				"category": row.category,
				"notes": row.notes,
				"days_offset": row.days_offset or 0,
				"scheduled_date": str(add_days(start, row.days_offset or 0)),
			}
		)

	return {"template_name": tmpl.template_name, "tasks": tasks}


@frappe.whitelist()
def spawn_template(template: str, property: str, start_date: str) -> dict:
	"""Spawn Home Maintenance tasks from a template for a given property.

	Each template task row becomes a separate Home Maintenance record with
	scheduled_date = start_date + days_offset.

	Args:
		template: Name of the Home Maintenance Template.
		property: Name of the Home Property.
		start_date: ISO date string — tasks are scheduled relative to this.

	Returns:
		dict with "created" (list of maintenance names) and "count".
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	tmpl = frappe.get_doc("Home Maintenance Template", template)
	start = getdate(start_date)
	created = []

	for task_row in tmpl.tasks:
		scheduled = add_days(start, task_row.days_offset or 0)
		doc = frappe.new_doc("Home Maintenance")
		doc.title = task_row.title
		doc.property = prop.name
		doc.household = prop.household
		doc.maintenance_type = "One-off"
		doc.category = task_row.category
		doc.status = "Scheduled"
		doc.scheduled_date = scheduled
		doc.notes = task_row.notes
		doc.insert()
		created.append(doc.name)

	return {"created": created, "count": len(created)}


@frappe.whitelist()
def duplicate_template(template: str) -> dict:
	"""Duplicate a template — creates an editable copy with is_system_template=0.

	Args:
		template: Name of the Home Maintenance Template to duplicate.

	Returns:
		dict with "name" of the new template.
	"""
	if not frappe.has_permission("Home Maintenance Template", "create"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	original = frappe.get_doc("Home Maintenance Template", template)

	new_doc = frappe.copy_doc(original)
	new_doc.template_name = _("Copy of {0}").format(original.template_name)
	new_doc.is_system_template = 0
	new_doc.insert()

	return {"name": new_doc.name}
