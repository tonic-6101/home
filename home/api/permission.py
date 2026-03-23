# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Household-scoped permission helpers.

Every Home DocType carries a `household` field. Access is granted only to
users who are members of that household (via Home Household Member).
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_user_households(user: str | None = None) -> list[str]:
	"""Return list of household names the user belongs to."""
	user = user or frappe.session.user

	return frappe.get_all(
		"Home Household Member",
		filters={"user": user},
		pluck="parent",
		ignore_permissions=True,
	)


def require_household_access(household: str, user: str | None = None) -> None:
	"""Raise PermissionError if user is not a member of the household."""
	user = user or frappe.session.user
	if user == "Administrator":
		return

	households = get_user_households(user)
	if household not in households:
		frappe.throw(
			_("You do not have access to this household"),
			frappe.PermissionError,
		)


def get_household_role(household: str, user: str | None = None) -> str | None:
	"""Return the user's role within a household: Owner / Adult / Child."""
	user = user or frappe.session.user
	roles = frappe.get_all(
		"Home Household Member",
		filters={"parent": household, "user": user},
		pluck="role",
		limit=1,
		ignore_permissions=True,
	)
	return roles[0] if roles else None


def require_role(household: str, min_role: str, user: str | None = None) -> None:
	"""Raise PermissionError if user's household role is below min_role.

	Role hierarchy: Owner > Adult > Child.
	"""
	hierarchy = {"Owner": 2, "Adult": 1, "Child": 0}
	user_role = get_household_role(household, user)

	if user_role is None:
		frappe.throw(
			_("You do not have access to this household"),
			frappe.PermissionError,
		)

	if hierarchy.get(user_role, -1) < hierarchy.get(min_role, 99):
		frappe.throw(
			_("You need at least {0} role for this action").format(min_role),
			frappe.PermissionError,
		)


def require_property_not_archived(property_name: str) -> None:
	"""Raise ValidationError if the property is archived.

	Call this in before_insert of child DocTypes (appliance, maintenance, etc.)
	to block new records on archived properties.
	"""
	is_archived = frappe.db.get_value("Home Property", property_name, "is_archived")
	if is_archived:
		frappe.throw(
			_("Cannot add records to an archived property"),
			frappe.ValidationError,
		)


# -- Frappe permission hooks (used in hooks.py) --


def get_household_condition(user: str | None = None) -> str:
	"""Permission query condition — restricts list queries to user's households."""
	user = user or frappe.session.user
	if user == "Administrator":
		return ""

	households = get_user_households(user)
	if not households:
		return "1=0"

	household_list = ", ".join(frappe.db.escape(h) for h in households)
	return f"`tabHome Property`.household in ({household_list})"


def has_household_permission(doc, ptype=None, user=None) -> bool:
	"""Per-document permission check — does the user belong to this doc's household?

	Also enforces role-based restrictions:
	- Child members cannot delete any records.
	"""
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	household = getattr(doc, "household", None)
	if not household:
		return False

	if household not in get_user_households(user):
		return False

	# Child members cannot delete records
	if ptype == "delete":
		role = get_household_role(household, user)
		if role == "Child":
			return False

	return True


@frappe.whitelist()
def get_my_role(household: str | None = None) -> dict:
	"""Return the current user's household role. Used by frontend for UI gating."""
	if not household:
		households = get_user_households()
		if not households:
			return {"role": None, "household": None}
		household = households[0]

	role = get_household_role(household)
	return {"role": role, "household": household}


@frappe.whitelist()
def has_app_permission() -> bool:
	"""Check if user has access to the Home app (is member of any household)."""
	return bool(get_user_households())
