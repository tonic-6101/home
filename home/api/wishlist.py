# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Improvement wishlist API.

Manages the household improvement wishlist — pre-commitment intentions
grouped by priority with estimated costs. Wishes can be converted to
tasks when the household is ready to act.
"""

from collections import defaultdict

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role


_WISH_TO_MAINTENANCE_CATEGORY = {
	"Cosmetic": "Painting & Decorating",
	"Structural": "Renovation & Building",
	"Energy Efficiency": "Renovation & Building",
	"Comfort": "General",
	"Safety": "General",
	"Garden": "Garden & Landscaping",
	"Technology": "General",
	"Other": "General",
}


def _map_wish_category(wish_category: str) -> str:
	"""Map a wish category to the closest maintenance category."""
	return _WISH_TO_MAINTENANCE_CATEGORY.get(wish_category, "General")


@frappe.whitelist()
def get_wishlist(property: str) -> dict:
	"""Return wishes for a property grouped by priority.

	Active wishes are grouped into Urgent / Important / Nice to have.
	Done and Abandoned wishes are returned separately.

	Args:
		property: Name of the Home Property record.

	Returns:
		dict with ``by_priority``, ``done``, ``abandoned``,
		``total_estimated``, ``items_without_estimate``, ``total_active``.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	wishes = frappe.get_all(
		"Home Improvement Wish",
		filters={"property": property},
		fields=[
			"name", "title", "category", "room", "priority",
			"estimated_cost", "status", "notes",
			"linked_task", "linked_orga_project",
		],
		order_by="priority asc, creation asc",
	)

	active = [w for w in wishes if w["status"] not in ("Done", "Abandoned")]
	done = [w for w in wishes if w["status"] == "Done"]
	abandoned = [w for w in wishes if w["status"] == "Abandoned"]

	total_estimated = sum(
		(w.get("estimated_cost") or 0) for w in active
	)
	items_without_estimate = sum(
		1 for w in active if not w.get("estimated_cost")
	)

	by_priority = defaultdict(list)
	priority_order = ["Urgent", "Important", "Nice to have"]
	for w in active:
		by_priority[w["priority"]].append(w)

	return {
		"by_priority": {p: by_priority[p] for p in priority_order if by_priority[p]},
		"done": done,
		"abandoned": abandoned,
		"total_estimated": total_estimated,
		"items_without_estimate": items_without_estimate,
		"total_active": len(active),
		"has_orga": "orga" in frappe.get_installed_apps(),
	}


@frappe.whitelist()
def convert_to_task(wish_name: str) -> dict:
	"""Create an Orga Task from a wishlist item.

	Pre-fills the task from the wish and links them.
	If the wish was already converted, returns the existing link.

	Args:
		wish_name: Name of the Home Improvement Wish record.

	Returns:
		dict with ``task`` name and ``already_exists`` flag.
	"""
	wish = frappe.get_doc("Home Improvement Wish", wish_name)
	require_household_access(wish.household)
	require_role(wish.household, "Adult")

	if wish.linked_task:
		return {"task": wish.linked_task, "already_exists": True}

	task = frappe.new_doc("Orga Task")
	task.subject = wish.title
	task.home_property = wish.property
	task.home_maintenance_category = _map_wish_category(wish.category)
	task.home_room = wish.room or ""
	task.description = wish.notes or ""
	task.status = "Open"
	task.assigned_to = frappe.session.user
	task.insert()

	frappe.db.set_value("Home Improvement Wish", wish_name, {
		"linked_task": task.name,
		"status": "Planned",
	})

	return {"task": task.name, "already_exists": False}


@frappe.whitelist()
def create_wish(
	property: str,
	title: str,
	category: str,
	priority: str,
	estimated_cost: float | None = None,
	room: str | None = None,
	notes: str | None = None,
) -> dict:
	"""Create a new improvement wish.

	Args:
		property: Name of the Home Property record.
		title: Wish title.
		category: Wish category (Cosmetic, Structural, etc.).
		priority: Priority level (Urgent, Important, Nice to have).
		estimated_cost: Optional rough cost estimate.
		room: Optional Home Room link.
		notes: Optional free-text notes.

	Returns:
		dict with ``name`` of the created wish.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	doc = frappe.new_doc("Home Improvement Wish")
	doc.property = property
	doc.title = title
	doc.category = category
	doc.priority = priority
	doc.status = "Wishlist"
	if estimated_cost is not None:
		doc.estimated_cost = estimated_cost
	if room:
		doc.room = room
	if notes:
		doc.notes = notes
	doc.insert()

	return {"name": doc.name}


@frappe.whitelist()
def update_wish(
	name: str,
	title: str | None = None,
	category: str | None = None,
	priority: str | None = None,
	estimated_cost: float | None = None,
	room: str | None = None,
	notes: str | None = None,
) -> dict:
	"""Update an existing improvement wish.

	Only provided fields are updated. Pass ``estimated_cost=0`` to clear.

	Returns:
		dict with ``ok`` flag.
	"""
	doc = frappe.get_doc("Home Improvement Wish", name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	if title is not None:
		doc.title = title
	if category is not None:
		doc.category = category
	if priority is not None:
		doc.priority = priority
	if estimated_cost is not None:
		doc.estimated_cost = estimated_cost or None
	if room is not None:
		doc.room = room
	if notes is not None:
		doc.notes = notes
	doc.save()

	return {"ok": True}


@frappe.whitelist()
def update_wish_status(name: str, status: str) -> dict:
	"""Change the status of a wish (Done, Abandoned, In Progress, etc.).

	Returns:
		dict with ``ok`` flag.
	"""
	valid = {"Wishlist", "Planned", "In Progress", "Done", "Abandoned"}
	if status not in valid:
		frappe.throw(_("Invalid status: {0}").format(status))

	doc = frappe.get_doc("Home Improvement Wish", name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	frappe.db.set_value("Home Improvement Wish", name, "status", status)
	return {"ok": True}


@frappe.whitelist()
def create_orga_from_wish(wish_name: str) -> dict:
	"""Create an Orga Project from a wishlist item.

	If a project is already linked, returns it without creating a duplicate.

	Returns:
		dict with ``orga_project`` name and ``already_exists`` flag.
	"""
	if "orga" not in frappe.get_installed_apps():
		frappe.throw(_("Orga is not installed"))

	wish = frappe.get_doc("Home Improvement Wish", wish_name)
	require_household_access(wish.household)
	require_role(wish.household, "Adult")

	if wish.linked_orga_project:
		return {"orga_project": wish.linked_orga_project, "already_exists": True}

	prop = frappe.get_doc("Home Property", wish.property)

	project = frappe.new_doc("Orga Project")
	project.title = wish.title
	project.description = wish.notes or ""
	project.status = "Planning"
	project.location = prop.city or ""
	project.source_app = "home"
	project.source_doctype = "Home Improvement Wish"
	project.source_name = wish.name
	project.insert()

	frappe.db.set_value("Home Improvement Wish", wish_name, {
		"linked_orga_project": project.name,
		"status": "Planned",
	})

	return {"orga_project": project.name, "already_exists": False}
