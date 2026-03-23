# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Frame guest portal integration (Feature 55).

Provides read-only property data via a UUID token — no Frappe login required.
The Frame app calls these endpoints to render guest pages.

Guest response excludes all financial data: no costs, no prices, no premiums,
no budget, no equity, no emergency info, no household members.
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_property_guest(frame_token: str) -> dict:
	"""Return property overview for Frame guest portal.

	Curated, read-only view suitable for tenants, house sitters, or buyers.
	No financial figures are included.

	Args:
		frame_token: UUID frame_token from Home Property.

	Returns:
		dict with property info, rooms, appliances, warranties,
		maintenance history, and insurance — all without cost data.
	"""
	if not frame_token:
		frappe.throw(_("Token is required"), frappe.PermissionError)

	property_name = frappe.db.get_value(
		"Home Property",
		{"frame_token": frame_token, "is_archived": 0},
		"name",
	)

	if not property_name:
		frappe.throw(_("Invalid or expired link"), frappe.PermissionError)

	prop = frappe.get_doc("Home Property", property_name)

	# Rooms
	rooms = frappe.get_all(
		"Home Room",
		filters={"property": property_name},
		fields=["room_name", "room_type"],
		order_by="room_name",
	)

	# Active items — no purchase price
	items = frappe.get_all(
		"Home Item",
		filters={"property": property_name, "item_type": "Appliance", "status": ["!=", "Disposed"]},
		fields=["item_name", "brand", "category", "status"],
		order_by="item_name",
	)

	# Warranties — no cost fields, enriched with appliance name
	warranties = frappe.get_all(
		"Home Warranty",
		filters={"property": property_name},
		fields=["name", "item", "warranty_type", "end_date"],
		order_by="end_date desc",
	)
	for w in warranties:
		if w.get("item"):
			w["item_name"] = frappe.db.get_value(
				"Home Item", w["item"], "item_name"
			) or ""
		else:
			w["item_name"] = ""
		del w["item"]

	# Completed maintenance — no cost, contractor resolved to name
	maintenance = frappe.get_all(
		"Home Maintenance",
		filters={"property": property_name, "status": "Completed"},
		fields=["title", "category", "completed_date", "contractor"],
		order_by="completed_date desc",
		limit=50,
	)
	for m in maintenance:
		if m.get("contractor"):
			m["contractor_name"] = frappe.db.get_value(
				"Contact", m["contractor"], "full_name"
			) or ""
		else:
			m["contractor_name"] = None
		del m["contractor"]

	# Active insurance — type, provider, renewal date only; no premium
	insurance = frappe.get_all(
		"Home Insurance Policy",
		filters={
			"property": property_name,
			"end_date": [">=", frappe.utils.today()],
		},
		fields=["policy_type", "provider", "end_date"],
	)

	return {
		"property_name": prop.property_name,
		"city": prop.city,
		"postal_code": prop.postal_code,
		"property_type": prop.property_type,
		"rooms": rooms,
		"items": items,
		"warranties": warranties,
		"maintenance": maintenance,
		"insurance": insurance,
	}
