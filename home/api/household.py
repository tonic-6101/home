# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Household management APIs — invite, remove, profile update."""

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role
from home.api.utils import _send_notification


@frappe.whitelist()
def create_household(household_name: str) -> dict:
	"""Create a new household for the current user.

	The current user is added as the Owner. Only allows creation if
	the user does not already belong to a household.
	"""
	user = frappe.session.user
	full_name = frappe.db.get_value("User", user, "full_name") or user

	from home.api.permission import get_user_households

	existing = get_user_households(user)
	if existing:
		frappe.throw(_("You already belong to a household"))

	household_name = (household_name or "").strip()
	if not household_name:
		household_name = _("{0}'s Home").format(full_name)

	hh = frappe.get_doc(
		{
			"doctype": "Home Household",
			"household_name": household_name,
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

	return {"name": hh.name, "household_name": hh.household_name}


@frappe.whitelist()
def invite_member(household: str, email: str, role: str) -> dict:
	"""Invite a user to a household by email.

	If the email matches an existing Frappe User, link them immediately.
	Otherwise, send a welcome invite — the User after_insert hook will
	auto-link them when they register.
	"""
	require_household_access(household)
	require_role(household, "Owner")

	if role not in ("Adult", "Child"):
		frappe.throw(_("Invited members can only have Adult or Child role"))

	email = email.strip().lower()

	doc = frappe.get_doc("Home Household", household)

	# Check for duplicate — already a member with this email or user
	for m in doc.members:
		if m.user and frappe.db.get_value("User", m.user, "email") == email:
			frappe.throw(_("{0} is already a member of this household").format(email))
		if m.email and m.email == email and not m.user:
			frappe.throw(_("An invitation for {0} is already pending").format(email))

	existing_user = frappe.db.get_value("User", {"email": email}, "name")

	if existing_user:
		full_name = frappe.db.get_value("User", existing_user, "full_name") or email
		doc.append(
			"members",
			{
				"display_name": full_name,
				"role": role,
				"user": existing_user,
				"email": email,
			},
		)
		doc.save(ignore_permissions=True)

		_send_notification(
			user=existing_user,
			title=_("You've been added to a household"),
			message=_("You are now a {0} member of {1}").format(role, doc.household_name),
			source_doctype="Home Household",
			source_name=household,
		)
	else:
		# Pending invitation — store email, no user link yet
		doc.append(
			"members",
			{
				"display_name": email.split("@")[0].title(),
				"role": role,
				"email": email,
			},
		)
		doc.save(ignore_permissions=True)

		# Send Frappe welcome/invite email
		frappe.sendmail(
			recipients=[email],
			subject=_("You're invited to join {0} on Home").format(doc.household_name),
			message=_(
				"You've been invited to join the household '{0}'. "
				"Create your account to get started."
			).format(doc.household_name),
		)

	return {"ok": True, "user_exists": bool(existing_user)}


@frappe.whitelist()
def remove_member(household: str, member_name: str) -> dict:
	"""Remove a member from a household. Only Owners can do this."""
	require_household_access(household)
	require_role(household, "Owner")

	doc = frappe.get_doc("Home Household", household)

	member_to_remove = None
	for m in doc.members:
		if m.name == member_name:
			member_to_remove = m
			break

	if not member_to_remove:
		frappe.throw(_("Member not found"))

	# Cannot remove yourself if you're the last Owner
	if member_to_remove.role == "Owner":
		owner_count = sum(1 for m in doc.members if m.role == "Owner")
		if owner_count <= 1:
			frappe.throw(_("Cannot remove the last Owner of a household"))

	doc.remove(member_to_remove)
	doc.save(ignore_permissions=True)

	return {"ok": True}


@frappe.whitelist()
def update_own_profile(
	household: str, display_name: str | None = None, avatar: str | None = None
) -> dict:
	"""Any member can update their own display name and avatar."""
	require_household_access(household)

	doc = frappe.get_doc("Home Household", household)
	user = frappe.session.user

	for m in doc.members:
		if m.user == user:
			if display_name is not None:
				m.display_name = display_name.strip()
			if avatar is not None:
				m.avatar = avatar
			doc.save(ignore_permissions=True)
			return {"ok": True}

	frappe.throw(_("You are not a member of this household"))


@frappe.whitelist()
def get_members(household: str) -> list[dict]:
	"""Return all members for a household the current user belongs to."""
	require_household_access(household)

	doc = frappe.get_doc("Home Household", household)
	members = []
	for m in doc.members:
		members.append(
			{
				"name": m.name,
				"display_name": m.display_name,
				"role": m.role,
				"user": m.user,
				"email": m.email,
				"avatar": m.avatar,
				"date_of_birth": str(m.date_of_birth) if m.date_of_birth else None,
				"pending": bool(m.email and not m.user),
			}
		)
	return members


@frappe.whitelist()
def change_member_role(household: str, member_name: str, new_role: str) -> dict:
	"""Change a member's role. Only Owners can do this."""
	require_household_access(household)
	require_role(household, "Owner")

	if new_role not in ("Owner", "Adult", "Child"):
		frappe.throw(_("Invalid role"))

	doc = frappe.get_doc("Home Household", household)

	for m in doc.members:
		if m.name == member_name:
			# Don't allow demoting last Owner
			if m.role == "Owner" and new_role != "Owner":
				owner_count = sum(1 for mem in doc.members if mem.role == "Owner")
				if owner_count <= 1:
					frappe.throw(_("Cannot demote the last Owner"))
			m.role = new_role
			doc.save(ignore_permissions=True)
			return {"ok": True}

	frappe.throw(_("Member not found"))


def link_user_to_pending_invitations(user_doc, method=None):
	"""Called on User after_insert — auto-link new user to any pending invitations."""
	email = user_doc.email.strip().lower()

	pending_members = frappe.get_all(
		"Home Household Member",
		filters={"email": email, "user": ("is", "not set")},
		fields=["name", "parent"],
	)

	for member in pending_members:
		frappe.db.set_value(
			"Home Household Member",
			member.name,
			{
				"user": user_doc.name,
				"display_name": user_doc.full_name or user_doc.email,
			},
		)

		# Trigger permission sync on the household
		household = frappe.get_doc("Home Household", member.parent)
		household.save(ignore_permissions=True)

		_send_notification(
			user=user_doc.name,
			title=_("Welcome to your household"),
			message=_("You've been added to {0}").format(household.household_name),
			source_doctype="Home Household",
			source_name=household.name,
		)
