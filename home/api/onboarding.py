# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Guided onboarding API (Feature 39).

Provides endpoints for checking and completing the per-user onboarding
tour. Each household member has their own onboarding_tour_completed flag
on the Home Household Member child table.
"""

import frappe
from frappe import _

from home.api.permission import require_household_access


@frappe.whitelist()
def get_onboarding_status(household: str) -> dict:
	"""Return the current user's onboarding status for the household.

	Args:
		household: Name of the Home Household record.

	Returns:
		dict with tour_completed, household_has_properties,
		user_is_creator, and variant.
	"""
	require_household_access(household)
	user = frappe.session.user

	household_doc = frappe.get_doc("Home Household", household)

	# Find current user's member row
	member = None
	for m in household_doc.members:
		if m.user == user:
			member = m
			break

	if not member:
		frappe.throw(
			_("You are not a member of this household"),
			frappe.PermissionError,
		)

	tour_completed = bool(member.onboarding_tour_completed)

	# Check if household has any properties
	has_properties = bool(
		frappe.db.count("Home Property", {"household": household})
	)

	# Check if user is the household creator (first Owner member)
	user_is_creator = household_doc.owner == user

	# Determine variant
	variant = "owner_setup" if member.role == "Owner" else "invited_member"

	# Find the household owner's display name for the member welcome tour
	owner_display_name = ""
	if variant == "invited_member":
		for m in household_doc.members:
			if m.role == "Owner":
				owner_display_name = m.display_name or ""
				break

	return {
		"tour_completed": tour_completed,
		"household_has_properties": has_properties,
		"user_is_creator": user_is_creator,
		"variant": variant,
		"owner_display_name": owner_display_name,
	}


@frappe.whitelist()
def complete_onboarding(household: str) -> dict:
	"""Mark the current user's onboarding tour as completed.

	Args:
		household: Name of the Home Household record.

	Returns:
		dict confirming completion.
	"""
	require_household_access(household)
	user = frappe.session.user

	household_doc = frappe.get_doc("Home Household", household)

	member = None
	for m in household_doc.members:
		if m.user == user:
			member = m
			break

	if not member:
		frappe.throw(
			_("You are not a member of this household"),
			frappe.PermissionError,
		)

	if member.onboarding_tour_completed:
		return {"already_completed": True}

	member.onboarding_tour_completed = 1
	household_doc.save(ignore_permissions=False)

	return {"already_completed": False}


@frappe.whitelist()
def reset_tour() -> dict:
	"""Reset the onboarding tour for the current user (re-trigger from Settings).

	Returns:
		dict with status.
	"""
	user = frappe.session.user

	members = frappe.get_all(
		"Home Household Member",
		filters={"user": user},
		fields=["name"],
		limit=1,
	)
	if not members:
		return {"status": "no_member_found"}

	frappe.db.set_value(
		"Home Household Member",
		members[0]["name"],
		"onboarding_tour_completed",
		0,
	)
	return {"status": "reset"}
