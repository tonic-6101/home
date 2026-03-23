# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Moving House Wizard API (Feature 46).

Manages a moving checklist on Home Property. System tasks are generated once,
and users can add custom tasks. Progress is computed as done / (total - skipped).
"""

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role

SYSTEM_TASKS = [
	# Before (10 tasks)
	{"title": "Notify current utility providers of move-out date", "category": "Utilities", "phase": "Before"},
	{"title": "Set up utilities at new property (electricity, gas, water)", "category": "Utilities", "phase": "Before"},
	{"title": "Arrange broadband / internet transfer or new connection", "category": "Technology", "phase": "Before"},
	{"title": "Update address with bank(s)", "category": "Finance", "phase": "Before"},
	{"title": "Update address with employer / payroll", "category": "Finance", "phase": "Before"},
	{"title": "Update address with tax authority", "category": "Finance", "phase": "Before"},
	{"title": "Redirect post", "category": "Admin", "phase": "Before"},
	{"title": "Notify home insurance — update to new address", "category": "Insurance", "phase": "Before"},
	{"title": "Arrange contents insurance for new property", "category": "Insurance", "phase": "Before"},
	{"title": "Book removals company", "category": "Logistics", "phase": "Before"},
	# Moving day (5 tasks)
	{"title": "Take meter readings at old property (gas, electricity, water)", "category": "Utilities", "phase": "Moving day"},
	{"title": "Take meter readings at new property", "category": "Utilities", "phase": "Moving day"},
	{"title": "Collect keys and check all locks work", "category": "Security", "phase": "Moving day"},
	{
		"title": "Locate water shutoff, electricity fuse box, and gas meter",
		"category": "Safety",
		"phase": "Moving day",
		"notes": "Add this to Home's emergency info once done",
	},
	{"title": "Change locks or request new keys from landlord", "category": "Security", "phase": "Moving day"},
	# After (8 tasks)
	{"title": "Update address with GP and dentist", "category": "Health", "phase": "After"},
	{"title": "Update driving licence address", "category": "Admin", "phase": "After"},
	{"title": "Register to vote at new address", "category": "Admin", "phase": "After"},
	{"title": "Update vehicle insurance and logbook", "category": "Finance", "phase": "After"},
	{"title": "Update address with children's school", "category": "Admin", "phase": "After"},
	{"title": "Introduce yourself to neighbours", "category": "Community", "phase": "After"},
	{"title": "Test smoke alarms and carbon monoxide detectors", "category": "Safety", "phase": "After"},
	{"title": "Add emergency contacts and shutoff locations to Home", "category": "Safety", "phase": "After"},
]

VALID_STATUSES = {"To do", "Done", "Skipped"}
PHASE_ORDER = ["Before", "Moving day", "After"]


def _compute_progress(tasks: list[dict]) -> dict:
	"""Compute progress stats for a list of tasks."""
	total = len(tasks)
	done = sum(1 for t in tasks if t.get("status") == "Done")
	skipped = sum(1 for t in tasks if t.get("status") == "Skipped")
	denominator = total - skipped
	progress_pct = round(done / denominator * 100) if denominator > 0 else 0
	return {
		"done": done,
		"total": total,
		"skipped": skipped,
		"progress_pct": progress_pct,
	}


def _tasks_to_list(doc) -> list[dict]:
	"""Convert child table rows to plain dicts."""
	return [
		{
			"idx": row.idx,
			"title": row.title,
			"category": row.category,
			"phase": row.phase,
			"status": row.status,
			"is_system_task": row.is_system_task,
			"notes": row.notes,
		}
		for row in doc.moving_checklist
	]


@frappe.whitelist()
def get_checklist(property: str) -> dict:
	"""Return the moving checklist grouped by phase with progress stats.

	Accessible to all household roles including Child (view-only).
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	tasks = _tasks_to_list(doc)

	by_phase = {}
	for phase in PHASE_ORDER:
		phase_tasks = [t for t in tasks if t["phase"] == phase]
		by_phase[phase] = {
			"tasks": phase_tasks,
			**_compute_progress(phase_tasks),
		}

	return {
		"by_phase": by_phase,
		"has_checklist": len(tasks) > 0,
		**_compute_progress(tasks),
	}


@frappe.whitelist()
def generate_checklist(property: str) -> dict:
	"""Generate or refresh the moving checklist for a property.

	Idempotent — appends missing system tasks without duplicating existing
	ones. Adult or Owner only.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	existing_titles = {row.title for row in (doc.moving_checklist or [])}

	added = 0
	for task in SYSTEM_TASKS:
		if task["title"] not in existing_titles:
			doc.append("moving_checklist", {
				"title": task["title"],
				"category": task["category"],
				"phase": task["phase"],
				"status": "To do",
				"is_system_task": 1,
				"notes": task.get("notes", ""),
			})
			added += 1

	if added:
		doc.save()

	return get_checklist(property)


@frappe.whitelist()
def update_task_status(property: str, idx: int, status: str) -> dict:
	"""Mark a moving task as Done, To do, or Skipped. Adult or Owner only."""
	if status not in VALID_STATUSES:
		frappe.throw(_("Invalid status: {0}. Must be one of: {1}").format(
			status, ", ".join(sorted(VALID_STATUSES))
		))

	idx = int(idx)
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	task_row = None
	for row in doc.moving_checklist:
		if row.idx == idx:
			task_row = row
			break

	if not task_row:
		frappe.throw(_("Task with idx {0} not found").format(idx))

	task_row.status = status
	doc.save()

	return get_checklist(property)


@frappe.whitelist()
def add_custom_task(property: str, title: str, phase: str, category: str = "Other") -> dict:
	"""Add a user-created task to the moving checklist. Adult or Owner only."""
	if phase not in PHASE_ORDER:
		frappe.throw(_("Invalid phase: {0}. Must be one of: {1}").format(
			phase, ", ".join(PHASE_ORDER)
		))

	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	doc.append("moving_checklist", {
		"title": title,
		"category": category,
		"phase": phase,
		"status": "To do",
		"is_system_task": 0,
	})
	doc.save()

	return get_checklist(property)
