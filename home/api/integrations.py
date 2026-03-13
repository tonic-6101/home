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
def create_tender_post(maintenance_name: str) -> dict:
	"""Create a Tender Post from a Home Maintenance record.

	Args:
		maintenance_name: Name of the Home Maintenance record.

	Returns:
		dict with tender_post name.
	"""
	if "tender" not in frappe.get_installed_apps():
		frappe.throw(_("Tender is not installed"))

	maintenance = frappe.get_doc("Home Maintenance", maintenance_name)
	property_doc = frappe.get_doc("Home Property", maintenance.property)

	post = frappe.new_doc("Tender Post")
	post.title = maintenance.title
	post.visibility = "Private"
	post.category = maintenance.category
	post.location = property_doc.city
	post.insert()

	# Store the back-link on the maintenance record
	frappe.db.set_value(
		"Home Maintenance", maintenance_name, "tender_post", post.name
	)

	return {"tender_post": post.name}


@frappe.whitelist()
def create_orga_project(maintenance_name: str) -> dict:
	"""Create an Orga Project from a Home Maintenance record.

	Args:
		maintenance_name: Name of the Home Maintenance record.

	Returns:
		dict with orga_project name.
	"""
	if "orga" not in frappe.get_installed_apps():
		frappe.throw(_("Orga is not installed"))

	maintenance = frappe.get_doc("Home Maintenance", maintenance_name)

	project = frappe.new_doc("Orga Project")
	project.project_name = maintenance.title
	project.description = maintenance.notes or ""
	project.insert()

	# Store the back-link on the maintenance record
	frappe.db.set_value(
		"Home Maintenance", maintenance_name, "orga_project", project.name
	)

	return {"orga_project": project.name}
