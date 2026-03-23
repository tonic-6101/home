# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Soft integration endpoints for Tender and Orga.

All functions check that the target app is installed before acting.
Buttons calling these endpoints are hidden (not disabled) in the UI
when the target app is absent.
"""

import frappe
from frappe import _


@frappe.whitelist()
def create_tender_post(maintenance: str) -> dict:
	"""Create a Tender Post from a Home Maintenance record.

	If a Tender Post is already linked, returns it without creating a duplicate.

	Args:
		maintenance: Name of the Home Maintenance record.

	Returns:
		dict with ``tender_post`` name and ``already_exists`` flag.
	"""
	from home.api.permission import require_household_access, require_role

	if "tender" not in frappe.get_installed_apps():
		frappe.throw(_("Tender is not installed"))

	task = frappe.get_doc("Home Maintenance", maintenance)
	prop = frappe.get_doc("Home Property", task.property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	if task.get("tender_post"):
		return {"tender_post": task.tender_post, "already_exists": True}

	post = frappe.new_doc("Tender Post")
	post.title = task.title
	post.description = task.notes or ""
	post.category = _map_category(task.category)
	post.location = prop.city or ""
	post.visibility = "Private"
	post.source_app = "home"
	post.source_doctype = "Home Maintenance"
	post.source_name = task.name
	post.insert()

	frappe.db.set_value("Home Maintenance", maintenance, "tender_post", post.name)

	return {"tender_post": post.name, "already_exists": False}


_CATEGORY_MAP = {
	"HVAC & Heating": "Heating",
	"Plumbing": "Plumbing",
	"Electrical": "Electrical",
	"Roofing & Gutters": "Roofing",
	"Carpentry": "Carpentry",
	"Painting & Decorating": "Decorating",
	"Cleaning": "Cleaning",
	"Garden & Landscaping": "Garden",
	"Pest Control": "Pest Control",
	"Inspection": "General",
	"General Repair": "General",
	"Other": "General",
}


def _map_category(home_category: str) -> str:
	"""Map a Home Maintenance category to a Tender Post category."""
	return _CATEGORY_MAP.get(home_category or "", "General")


@frappe.whitelist()
def create_orga_project(maintenance_name: str) -> dict:
	"""Create an Orga Project from a Home Maintenance record.

	Pre-fills the project with task title, notes, property city.
	Returns existing project if already linked (idempotent).
	"""
	from home.api.permission import require_household_access, require_role

	if "orga" not in frappe.get_installed_apps():
		frappe.throw(_("Orga is not installed"))

	task = frappe.get_doc("Home Maintenance", maintenance_name)
	prop = frappe.get_doc("Home Property", task.property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	if task.get("orga_project"):
		return {"orga_project": task.orga_project, "already_exists": True}

	project = frappe.new_doc("Orga Project")
	project.title = task.title
	project.description = task.notes or ""
	project.status = "Planning"
	project.location = prop.city or ""
	project.source_app = "home"
	project.source_doctype = "Home Maintenance"
	project.source_name = task.name
	project.insert()

	frappe.db.set_value(
		"Home Maintenance", maintenance_name, "orga_project", project.name
	)

	return {"orga_project": project.name, "already_exists": False}
