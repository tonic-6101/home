# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Room management API — Feature 3.

Rooms organise appliances and inventory by location within a property.
"""

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role


@frappe.whitelist()
def get_rooms(property: str) -> list[dict]:
	"""Return all rooms for a property with computed counts."""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	rooms = frappe.get_all(
		"Home Room",
		filters={"property": property},
		fields=["name", "room_name", "room_type", "area_sqm", "sort_order", "notes"],
		order_by="sort_order asc",
	)

	for room in rooms:
		room["item_count"] = frappe.db.count(
			"Home Item", {"room": room["name"], "status": ["!=", "Disposed"]}
		)
		room["open_task_count"] = frappe.db.count(
			"Orga Task",
			{"home_room": room["name"], "status": ["not in", ["Completed", "Cancelled"]]},
		)

	return rooms


@frappe.whitelist()
def get_unassigned_counts(property: str) -> dict:
	"""Return counts of appliances and inventory with no room assigned."""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	return {
		"item_count": frappe.db.count(
			"Home Item",
			{"property": property, "room": ["is", "not set"]},
		),
	}


@frappe.whitelist()
def create_room(
	property: str,
	room_name: str,
	room_type: str = "",
	area_sqm: float | None = None,
) -> dict:
	"""Create a new room in a property."""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	# Determine sort_order — append after the last room
	last_order = (
		frappe.db.get_value(
			"Home Room",
			{"property": property},
			"sort_order",
			order_by="sort_order desc",
		)
		or 0
	)

	room = frappe.get_doc(
		{
			"doctype": "Home Room",
			"property": property,
			"household": doc.household,
			"room_name": room_name,
			"room_type": room_type,
			"area_sqm": area_sqm,
			"sort_order": last_order + 10,
		}
	)
	room.insert()

	return room.as_dict()


@frappe.whitelist()
def update_room(
	name: str,
	room_name: str | None = None,
	room_type: str | None = None,
	area_sqm: float | None = None,
	notes: str | None = None,
) -> dict:
	"""Update room details."""
	room = frappe.get_doc("Home Room", name)
	require_household_access(room.household)

	if room_name is not None:
		room.room_name = room_name
	if room_type is not None:
		room.room_type = room_type
	if area_sqm is not None:
		room.area_sqm = area_sqm
	if notes is not None:
		room.notes = notes

	room.save()
	return room.as_dict()


@frappe.whitelist()
def reorder_rooms(property: str, order: list | str) -> None:
	"""Update sort_order for rooms in bulk.

	Args:
		property: Property name for access check.
		order: Ordered list of room names (JSON string or list).
	"""
	import json

	if isinstance(order, str):
		order = json.loads(order)

	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	for idx, room_name in enumerate(order):
		frappe.db.set_value(
			"Home Room",
			room_name,
			"sort_order",
			(idx + 1) * 10,
			update_modified=False,
		)

	frappe.db.commit()


@frappe.whitelist()
def delete_room(name: str, move_to: str | None = None) -> None:
	"""Delete a room, reassigning linked records first.

	Args:
		name: Room to delete.
		move_to: Room name to receive orphaned records, or None for Unassigned.
	"""
	room = frappe.get_doc("Home Room", name)
	require_household_access(room.household)
	require_role(room.household, "Owner")

	target = move_to or None

	# Validate move_to target exists and belongs to the same property
	if target:
		target_room = frappe.get_doc("Home Room", target)
		if target_room.property != room.property:
			frappe.throw(_("Target room must be in the same property"))

	# Reassign linked items
	frappe.db.set_value(
		"Home Item",
		{"room": name},
		"room",
		target,
		update_modified=False,
	)

	frappe.delete_doc("Home Room", name, ignore_permissions=True)


@frappe.whitelist()
def get_room_counts(name: str) -> dict:
	"""Return counts of linked records for a room (used by delete dialog)."""
	room = frappe.get_doc("Home Room", name)
	require_household_access(room.household)

	return {
		"item_count": frappe.db.count("Home Item", {"room": name}),
	}


@frappe.whitelist()
def suggest_rooms(property_type: str) -> list[dict]:
	"""Return suggested rooms for a property type (used on first property setup)."""
	suggestions = {
		"House": [
			{"room_name": "Kitchen", "room_type": "Kitchen"},
			{"room_name": "Living Room", "room_type": "Living Room"},
			{"room_name": "Bedroom", "room_type": "Bedroom"},
			{"room_name": "Bathroom", "room_type": "Bathroom"},
			{"room_name": "Garage", "room_type": "Garage"},
		],
		"Apartment": [
			{"room_name": "Kitchen", "room_type": "Kitchen"},
			{"room_name": "Living Room", "room_type": "Living Room"},
			{"room_name": "Bedroom", "room_type": "Bedroom"},
			{"room_name": "Bathroom", "room_type": "Bathroom"},
		],
		"Studio": [
			{"room_name": "Kitchen", "room_type": "Kitchen"},
			{"room_name": "Bathroom", "room_type": "Bathroom"},
		],
	}

	return suggestions.get(property_type, [])
