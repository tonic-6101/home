# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Frame guest portal integration.

Provides read-only property data via a UUID token — no Frappe login required.
The Frame app calls these endpoints to render guest pages.
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_property_guest(token: str) -> dict:
	"""Return property overview for Frame guest portal.

	Args:
		token: UUID frame_token from Home Property.

	Returns:
		Property data with appliance list and recent maintenance history.
	"""
	if not token:
		frappe.throw(_("Token is required"), frappe.AuthenticationError)

	property_doc = frappe.db.get_value(
		"Home Property",
		{"frame_token": token},
		["name", "property_name", "property_type", "city", "area_sqm"],
		as_dict=True,
	)

	if not property_doc:
		frappe.throw(_("Invalid or expired token"), frappe.AuthenticationError)

	appliances = frappe.get_all(
		"Home Appliance",
		filters={"property": property_doc.name, "status": ["!=", "Disposed"]},
		fields=["appliance_name", "category", "brand", "model", "status"],
	)

	maintenance = frappe.get_all(
		"Home Maintenance",
		filters={"property": property_doc.name},
		fields=["title", "category", "status", "completed_date"],
		order_by="completed_date desc",
		limit=20,
	)

	return {
		"property": property_doc,
		"appliances": appliances,
		"recent_maintenance": maintenance,
	}
