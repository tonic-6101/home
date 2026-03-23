# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Photo documentation API (Feature 59).

Manages photos attached to properties, rooms, items, and maintenance tasks.
Gallery views, before/after pairs, and timeline.
"""

import frappe
from frappe import _
from frappe.utils import today

from home.api.permission import require_household_access


@frappe.whitelist()
def get_photos(
	property: str,
	purpose: str = "",
	room: str = "",
	item: str = "",
	maintenance: str = "",
) -> list[dict]:
	"""Return photos for a property with optional filters.

	Args:
		property: Name of the Home Property record.
		purpose: Filter by purpose (General, Condition, Damage, etc.).
		room: Filter by room name.
		item: Filter by item name.
		maintenance: Filter by maintenance name.

	Returns:
		List of photo dicts sorted by photo_date desc.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	filters: dict = {"property": property}
	if purpose:
		filters["purpose"] = purpose
	if room:
		filters["room"] = room
	if item:
		filters["item"] = item
	if maintenance:
		filters["maintenance"] = maintenance

	photos = frappe.get_all(
		"Home Photo",
		filters=filters,
		fields=[
			"name", "photo", "caption", "purpose", "photo_date",
			"room", "item", "maintenance", "before_after", "pair_ref", "notes",
		],
		order_by="photo_date desc, creation desc",
		limit_page_length=200,
	)

	return photos


@frappe.whitelist()
def create_photo(
	property: str,
	photo: str,
	purpose: str = "General",
	caption: str = "",
	photo_date: str = "",
	room: str = "",
	item: str = "",
	maintenance: str = "",
	before_after: str = "",
	pair_ref: str = "",
	notes: str = "",
) -> dict:
	"""Create a new photo record.

	Args:
		property: Name of the Home Property record.
		photo: URL of the uploaded image file.
		purpose: Photo purpose (General, Condition, Damage, Renovation, Move-in, Move-out).
		caption: Short description.
		photo_date: When the photo was taken (defaults to today).
		room: Optional room link.
		item: Optional item link.
		maintenance: Optional maintenance link.
		before_after: Before/After for Renovation purpose.
		pair_ref: Name of paired photo for before/after.
		notes: Additional notes.

	Returns:
		dict with the created photo's name and photo URL.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	resolved_pair_ref = ""
	if purpose == "Renovation":
		resolved_pair_ref = pair_ref
		# Auto-pair: if uploading "After" with no explicit pair_ref,
		# find the most recent unpaired "Before" for the same property/room/item.
		if before_after == "After" and not resolved_pair_ref:
			resolved_pair_ref = _find_unpaired_before(property, room, item)
		elif before_after == "Before" and not resolved_pair_ref:
			resolved_pair_ref = _find_unpaired_after(property, room, item)

	photo_doc = frappe.get_doc({
		"doctype": "Home Photo",
		"property": property,
		"photo": photo,
		"purpose": purpose,
		"caption": caption,
		"photo_date": photo_date or today(),
		"room": room or None,
		"item": item or None,
		"maintenance": maintenance or None,
		"before_after": before_after if purpose == "Renovation" else "",
		"pair_ref": resolved_pair_ref,
		"notes": notes,
	})
	photo_doc.insert()

	return {"name": photo_doc.name, "photo": photo_doc.photo}


def _find_unpaired_before(property: str, room: str, item: str) -> str:
	"""Find the most recent unpaired Renovation 'Before' photo for the same scope."""
	filters: dict = {
		"property": property,
		"purpose": "Renovation",
		"before_after": "Before",
		"pair_ref": ("in", ["", None]),
	}
	if room:
		filters["room"] = room
	if item:
		filters["item"] = item

	match = frappe.get_all(
		"Home Photo",
		filters=filters,
		fields=["name"],
		order_by="photo_date desc, creation desc",
		limit_page_length=1,
	)
	return match[0].name if match else ""


def _find_unpaired_after(property: str, room: str, item: str) -> str:
	"""Find the most recent unpaired Renovation 'After' photo for the same scope."""
	filters: dict = {
		"property": property,
		"purpose": "Renovation",
		"before_after": "After",
		"pair_ref": ("in", ["", None]),
	}
	if room:
		filters["room"] = room
	if item:
		filters["item"] = item

	match = frappe.get_all(
		"Home Photo",
		filters=filters,
		fields=["name"],
		order_by="photo_date desc, creation desc",
		limit_page_length=1,
	)
	return match[0].name if match else ""


@frappe.whitelist()
def get_unpaired_photos(
	property: str,
	before_after: str = "Before",
	room: str = "",
	item: str = "",
) -> list[dict]:
	"""Return unpaired Renovation photos for pairing selection in the UI.

	Args:
		property: Name of the Home Property record.
		before_after: Which side to find ('Before' or 'After').
		room: Optional room filter.
		item: Optional item filter.

	Returns:
		List of unpaired photo dicts.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	filters: dict = {
		"property": property,
		"purpose": "Renovation",
		"before_after": before_after,
		"pair_ref": ("in", ["", None]),
	}
	if room:
		filters["room"] = room
	if item:
		filters["item"] = item

	return frappe.get_all(
		"Home Photo",
		filters=filters,
		fields=["name", "photo", "caption", "photo_date", "room", "item"],
		order_by="photo_date desc, creation desc",
		limit_page_length=50,
	)


@frappe.whitelist()
def delete_photo(name: str) -> None:
	"""Delete a photo record.

	Args:
		name: Name of the Home Photo record.
	"""
	doc = frappe.get_doc("Home Photo", name)
	require_household_access(doc.household)
	doc.delete()
