# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Soft integration endpoints (Tender, Orga).

Creates records in peer apps when available. Always checks app presence
first so Home works without optional dependencies.
"""

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role


# ---------------------------------------------------------------------------
# Category mapping (Home maintenance category -> Tender category)
# ---------------------------------------------------------------------------

_HOME_TO_TENDER_CATEGORY = {
	"HVAC & Heating": "Heating",
	"Plumbing": "Plumbing",
	"Electrical": "Electrical",
	"Roofing & Gutters": "Roofing",
	"Carpentry": "Carpentry",
	"Painting & Decorating": "Decorating",
	"Cleaning": "Cleaning",
	"Garden & Landscaping": "Garden",
	"Pest Control": "Pest Control",
}


def _map_category(category: str | None) -> str:
	"""Map a Home maintenance category to the closest Tender category."""
	if not category:
		return "General"
	return _HOME_TO_TENDER_CATEGORY.get(category, "General")


# ---------------------------------------------------------------------------
# Tender integration
# ---------------------------------------------------------------------------

@frappe.whitelist(methods=["POST"])
def create_tender_post(maintenance: str) -> dict:
	"""Create a Tender Post from an Orga Task with Home context.

	The Orga Task must have ``home_property`` set (Home maintenance task).
	If a tender_post is already linked, returns it without creating a new one.

	Args:
		maintenance: Name of the Orga Task record.

	Returns:
		dict with ``tender_post`` name and ``already_exists`` flag.
	"""
	if "tender" not in frappe.get_installed_apps():
		frappe.throw(_("Tender is not installed"))

	task = frappe.get_doc("Orga Task", maintenance)

	# Permission: require Home household access (Adult+)
	if task.home_property:
		prop = frappe.get_doc("Home Property", task.home_property)
		require_household_access(prop.household)
		require_role(prop.household, "Adult")

	# Idempotent: return existing link
	existing = frappe.db.get_value("Orga Task", maintenance, "tender_post")
	if existing:
		return {"tender_post": existing, "already_exists": True}

	# Resolve location from property
	location = ""
	if task.home_property:
		location = frappe.db.get_value(
			"Home Property", task.home_property, "city"
		) or ""

	post = frappe.new_doc("Tender Post")
	post.title = task.subject or ""
	post.description = task.description or ""
	post.category = _map_category(task.home_maintenance_category)
	post.location = location
	post.visibility = "Private"
	post.source_app = "home"
	post.source_doctype = "Orga Task"
	post.source_name = maintenance
	post.insert()

	# Back-link
	frappe.db.set_value("Orga Task", maintenance, "tender_post", post.name)

	return {"tender_post": post.name, "already_exists": False}


# ---------------------------------------------------------------------------
# Orga Project integration
# ---------------------------------------------------------------------------

@frappe.whitelist(methods=["POST"])
def create_orga_project(maintenance_name: str) -> dict:
	"""Create an Orga Project from an Orga Task with Home context.

	If a project is already linked, returns it without creating a new one.

	Args:
		maintenance_name: Name of the Orga Task record.

	Returns:
		dict with ``orga_project`` name and ``already_exists`` flag.
	"""
	if "orga" not in frappe.get_installed_apps():
		frappe.throw(_("Orga is not installed"))

	task = frappe.get_doc("Orga Task", maintenance_name)

	if task.home_property:
		prop = frappe.get_doc("Home Property", task.home_property)
		require_household_access(prop.household)
		require_role(prop.household, "Adult")

	# Idempotent: return existing link
	if task.project:
		return {"orga_project": task.project, "already_exists": True}

	location = ""
	if task.home_property:
		location = frappe.db.get_value(
			"Home Property", task.home_property, "city"
		) or ""

	project = frappe.new_doc("Orga Project")
	project.project_name = task.subject or ""
	project.description = task.description or ""
	project.status = "Open"
	project.source_app = "home"
	project.source_doctype = "Orga Task"
	project.source_name = maintenance_name
	project.insert()

	# Link task to project
	frappe.db.set_value("Orga Task", maintenance_name, "project", project.name)

	return {"orga_project": project.name, "already_exists": False}
