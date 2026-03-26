# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Property management and dashboard APIs."""

import frappe
from frappe import _
from frappe.utils import add_days, today

from home.api.permission import (
	get_household_role,
	get_user_households,
	require_household_access,
	require_role,
)


def _safe_count(doctype: str, filters: dict | None = None, **kwargs) -> int:
	"""Count records, returning 0 if the table doesn't exist yet."""
	try:
		return frappe.db.count(doctype, filters, **kwargs)
	except Exception:
		return 0


def _safe_get_value(doctype: str, filters: dict, fieldname: str, **kwargs):
	"""Get a field value, returning None if the table doesn't exist yet."""
	try:
		return frappe.db.get_value(doctype, filters, fieldname, **kwargs)
	except Exception:
		return None


def _safe_get_all(doctype: str, **kwargs) -> list:
	"""Get all records, returning [] if the table doesn't exist yet."""
	try:
		return frappe.get_all(doctype, **kwargs)
	except Exception:
		return []


# ---------------------------------------------------------------------------
# Feature 2 — Property Management
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_property(name: str) -> dict:
	"""Return full property data with computed stats and household members."""
	doc = frappe.get_doc("Home Property", name)
	require_household_access(doc.household)

	return {
		**doc.as_dict(),
		"item_count": _safe_count(
			"Home Item", {"property": name, "status": ["!=", "Disposed"]}
		),
		"open_maintenance_count": _safe_count(
			"Orga Task",
			{"home_property": name, "status": ["not in", ["Completed", "Cancelled"]]},
		),
		"upcoming_warranty_expiry": _safe_get_value(
			"Home Warranty",
			{"property": name, "end_date": [">=", today()]},
			"end_date",
			order_by="end_date asc",
		),
		"members": frappe.get_all(
			"Home Household Member",
			filters={"parent": doc.household},
			fields=["display_name", "role", "avatar", "user"],
			ignore_permissions=True,
		),
	}


@frappe.whitelist()
def create_property(
	property_name: str,
	property_type: str,
	ownership_status: str,
	household: str | None = None,
) -> dict:
	"""Create a property, auto-creating a household if the user has none.

	First property: silently creates a household named "{Full Name}'s Home".
	Subsequent: links to the specified household (or the user's sole household).
	"""
	user = frappe.session.user
	user_households = get_user_households(user)

	if household:
		require_household_access(household)
	elif not user_households:
		full_name = frappe.db.get_value("User", user, "full_name") or user
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": _("{0}'s Home").format(full_name),
				"members": [
					{
						"display_name": full_name,
						"role": "Owner",
						"user": user,
					}
				],
			}
		)
		hh.insert(ignore_permissions=True)
		household = hh.name

		# Assign Home Manager role so user can access Home DocTypes
		if not frappe.db.exists(
			"Has Role", {"parent": user, "role": "Home Manager"}
		):
			user_doc = frappe.get_doc("User", user)
			user_doc.append("roles", {"role": "Home Manager"})
			user_doc.save(ignore_permissions=True)
	elif len(user_households) == 1:
		household = user_households[0]
	else:
		frappe.throw(
			_("You belong to multiple households — please specify which one"),
			frappe.ValidationError,
		)

	# Community tier: one active property per household
	if "home_pro" not in frappe.get_installed_apps():
		existing = frappe.db.count(
			"Home Property",
			{"household": household, "is_archived": 0},
		)
		if existing >= 1:
			frappe.throw(
				_("Your household already has a property. "
				  "You can edit it from the dashboard."),
				frappe.ValidationError,
			)

	prop = frappe.get_doc(
		{
			"doctype": "Home Property",
			"household": household,
			"property_name": property_name,
			"property_type": property_type,
			"ownership_status": ownership_status,
		}
	)
	prop.insert()

	return {"name": prop.name, "household": household}


@frappe.whitelist()
def archive_property(name: str) -> None:
	"""Archive a property. Owner only."""
	prop = frappe.get_doc("Home Property", name)
	require_household_access(prop.household)
	require_role(prop.household, "Owner")

	if prop.is_archived:
		frappe.throw(_("Property is already archived"))

	prop.is_archived = 1
	prop.save()


@frappe.whitelist()
def unarchive_property(name: str) -> None:
	"""Unarchive a property. Owner only."""
	prop = frappe.get_doc("Home Property", name)
	require_household_access(prop.household)
	require_role(prop.household, "Owner")

	if not prop.is_archived:
		frappe.throw(_("Property is not archived"))

	prop.is_archived = 0
	prop.save()


@frappe.whitelist()
def update_property(name: str, **kwargs) -> dict:
	"""Update property fields. Owner only."""
	doc = frappe.get_doc("Home Property", name)
	require_household_access(doc.household)
	require_role(doc.household, "Owner")

	allowed_fields = {
		"property_name",
		"property_type",
		"ownership_status",
		"cover_image",
		"address_line1",
		"address_line2",
		"city",
		"postal_code",
		"country",
		"purchase_date",
		"move_in_date",
		"area_sqm",
		"notes",
	}

	for field, value in kwargs.items():
		if field in allowed_fields:
			setattr(doc, field, value)

	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def list_properties(
	household: str | None = None, include_archived: bool = False
) -> list[dict]:
	"""Return properties for the current user's household(s)."""
	user_households = get_user_households()
	if not user_households:
		return []

	if household:
		require_household_access(household)
		households = [household]
	else:
		households = user_households

	filters: dict = {"household": ["in", households]}
	if not include_archived:
		filters["is_archived"] = 0

	properties = frappe.get_all(
		"Home Property",
		filters=filters,
		fields=[
			"name",
			"property_name",
			"property_type",
			"ownership_status",
			"cover_image",
			"city",
			"is_archived",
			"household",
		],
		order_by="creation desc",
	)

	for prop in properties:
		prop["item_count"] = _safe_count(
			"Home Item",
			{"property": prop["name"], "status": ["!=", "Disposed"]},
		)
		prop["open_maintenance_count"] = _safe_count(
			"Orga Task",
			{
				"home_property": prop["name"],
				"status": ["not in", ["Completed", "Cancelled"]],
			},
		)
		prop["upcoming_warranty_expiry"] = _safe_get_value(
			"Home Warranty",
			{"property": prop["name"], "end_date": [">=", today()]},
			"end_date",
			order_by="end_date asc",
		)

	return properties


# ---------------------------------------------------------------------------
# Feature 19 — Emergency Info
# ---------------------------------------------------------------------------


@frappe.whitelist()
def update_emergency_info(name: str, **kwargs) -> dict:
	"""Update emergency info fields on a property. Adult+ role required.

	Emergency info is the one area where Adults (not just Owners) can edit
	property fields. Accepts shutoff locations, alarm/evacuation notes,
	building manager phone, and emergency_contacts child table rows.
	"""
	doc = frappe.get_doc("Home Property", name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	allowed_fields = {
		"gas_shutoff_location",
		"water_shutoff_location",
		"electricity_shutoff_location",
		"alarm_notes",
		"evacuation_notes",
		"building_manager_phone",
		"emergency_notes",
	}

	for field, value in kwargs.items():
		if field in allowed_fields:
			setattr(doc, field, value)

	# Handle emergency_contacts child table
	if "emergency_contacts" in kwargs:
		doc.emergency_contacts = []
		for row in kwargs["emergency_contacts"]:
			doc.append("emergency_contacts", {
				"role": row.get("role"),
				"contact_name": row.get("contact_name"),
				"phone": row.get("phone"),
				"available": row.get("available"),
				"notes": row.get("notes"),
			})

	doc.save(ignore_permissions=True)
	return doc.as_dict()


# ---------------------------------------------------------------------------
# Feature 4 — Property Dashboard
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_dashboard(property: str) -> dict:
	"""Return all data the property dashboard needs in a single call.

	Includes: property doc, stats bar, upcoming maintenance/warranties,
	recent activity, household members, and role-gated financial widget flag.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	role = get_household_role(doc.household)

	upcoming_maintenance = _safe_get_all(
		"Orga Task",
		filters={
			"home_property": property,
			"status": ["not in", ["Completed", "Cancelled"]],
		},
		fields=["name", "subject as title", "start_date as scheduled_date", "home_contractor as contractor", "status"],
		order_by="start_date asc",
		limit=3,
	)

	upcoming_warranties = _safe_get_all(
		"Home Warranty",
		filters={
			"property": property,
			"end_date": ["between", [today(), add_days(today(), 90)]],
		},
		fields=["name", "item", "warranty_type", "end_date"],
		order_by="end_date asc",
		limit=2,
	)

	activity = _get_recent_activity(property, limit=7)

	rooms = _safe_get_all(
		"Home Room",
		filters={"property": property},
		fields=["name", "room_name", "room_type", "sort_order"],
		order_by="sort_order asc, creation asc",
	)
	# Enrich rooms with appliance and open task counts
	for room in rooms:
		room["item_count"] = _safe_count(
			"Home Item",
			{"room": room["name"], "status": ["!=", "Disposed"]},
		)
		room["open_task_count"] = _safe_count(
			"Orga Task",
			{
				"home_room": room["name"],
				"status": ["not in", ["Completed", "Cancelled"]],
			},
		)

	members = frappe.get_all(
		"Home Household Member",
		filters={"parent": doc.household},
		fields=["display_name", "role", "avatar", "user"],
		ignore_permissions=True,
	)

	result = {
		"property": doc.as_dict(),
		"role": role,
		"stats": {
			"item_count": _safe_count(
				"Home Item",
				{"property": property, "status": ["!=", "Disposed"]},
			),
			"open_task_count": _safe_count(
				"Orga Task",
				{
					"home_property": property,
					"status": ["not in", ["Completed", "Cancelled"]],
				},
			),
			"upcoming_warranty_expiry": _safe_get_value(
				"Home Warranty",
				{"property": property, "end_date": [">=", today()]},
				"end_date",
				order_by="end_date asc",
			),
		},
		"upcoming_maintenance": upcoming_maintenance,
		"upcoming_warranties": upcoming_warranties,
		"rooms": rooms,
		"recent_activity": activity,
		"members": members,
		"show_financial_widgets": role in ("Owner", "Adult"),
	}

	return result


def _get_recent_activity(property: str, limit: int = 7) -> list:
	"""Unified recent activity across household DocTypes for this property.

	Tracks: appliances, maintenance, warranties, inventory items, rooms.
	Excludes system-generated records (auto-created recurring maintenance)
	and entries not modified by a real household member.
	"""
	# Get household member users for filtering
	household = frappe.db.get_value("Home Property", property, "household")
	member_users = set(
		frappe.get_all(
			"Home Household Member",
			filters={"parent": household, "user": ["is", "set"]},
			pluck="user",
			ignore_permissions=True,
		)
	)

	tracked = [
		(
			"Home Item",
			["name", "item_name as title", "modified", "modified_by", "owner"],
			{"property": property},
		),
		(
			"Orga Task",
			["name", "subject as title", "modified", "modified_by", "owner"],
			# Exclude auto-created recurring occurrences: owner = Administrator
			# means system-generated, not user-initiated
			{"home_property": property, "owner": ["!=", "Administrator"]},
		),
		(
			"Home Warranty",
			["name", "item as title", "modified", "modified_by", "owner"],
			{"property": property},
		),
		(
			"Home Room",
			["name", "room_name as title", "modified", "modified_by", "owner"],
			{"property": property},
		),
	]

	entries = []
	for doctype, fields, extra_filters in tracked:
		filters = {**extra_filters}
		rows = _safe_get_all(
			doctype,
			filters=filters,
			fields=fields,
			order_by="modified desc",
			limit=limit,
		)
		for row in rows:
			row["doctype"] = doctype
		entries.extend(rows)

	# Only include entries modified by a real household member
	entries = [e for e in entries if e.get("modified_by") in member_users]

	entries.sort(key=lambda x: x["modified"], reverse=True)
	return entries[:limit]
