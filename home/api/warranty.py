# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Warranty tracking APIs (Features 8–10).

Endpoints for listing warranties per appliance, retrieving full warranty
detail with claim history, adding/updating claims, and computing expiry
status at read time.
"""

import frappe
from frappe import _
from frappe.utils import date_diff, today

from home.api.permission import (
	get_household_role,
	require_household_access,
	require_role,
)


def _compute_expiry_status(end_date: str) -> tuple[str, int]:
	"""Compute expiry status and days remaining from end_date.

	Returns:
		Tuple of (status, days_remaining) where status is one of
		'active', 'expiring_soon', or 'expired'.
	"""
	days_left = date_diff(end_date, today())
	if days_left < 0:
		return "expired", 0
	if days_left <= 90:
		return "expiring_soon", days_left
	return "active", days_left


@frappe.whitelist()
def get_warranties(item: str) -> dict:
	"""Return all warranties for an item with computed expiry status.

	Args:
		item: Name of the Home Item record.

	Returns:
		dict with "warranties" list ordered by end_date desc.
	"""
	doc = frappe.get_doc("Home Item", item)
	require_household_access(doc.household)

	warranties = frappe.get_all(
		"Home Warranty",
		filters={"item": item},
		fields=[
			"name",
			"warranty_type",
			"provider",
			"start_date",
			"end_date",
			"document",
		],
		order_by="end_date desc",
	)

	for w in warranties:
		w["expiry_status"], w["days_remaining"] = _compute_expiry_status(w["end_date"])

		# Claim summary for card display
		w["claim_count"] = frappe.db.count(
			"Home Warranty Claim", {"parent": w["name"]}
		)
		if w["claim_count"]:
			latest = frappe.get_all(
				"Home Warranty Claim",
				filters={"parent": w["name"]},
				fields=["outcome"],
				order_by="claim_date desc",
				limit=1,
			)
			w["last_claim_outcome"] = latest[0].outcome if latest else None
		else:
			w["last_claim_outcome"] = None

	return {"warranties": warranties}


@frappe.whitelist()
def get_warranty(name: str) -> dict:
	"""Return full warranty detail including claim history.

	Strips financial claim data (amount_reimbursed) for Child role.

	Args:
		name: Name of the Home Warranty record.

	Returns:
		dict with all warranty fields, expiry_status, days_remaining,
		and claims list.
	"""
	doc = frappe.get_doc("Home Warranty", name)
	require_household_access(doc.household)

	result = doc.as_dict()

	result["expiry_status"], result["days_remaining"] = _compute_expiry_status(
		doc.end_date
	)

	# Include caller's household role for frontend gating
	role = get_household_role(doc.household)
	result["user_role"] = role

	# Strip financial claim data for Child role
	if role == "Child":
		for claim in result.get("claims", []):
			claim.pop("amount_reimbursed", None)

	return result


@frappe.whitelist()
def get_property_warranties(property: str) -> dict:
	"""Return all warranties for a property with computed expiry status.

	Useful for the property dashboard upcoming warranty expiry widget.

	Args:
		property: Name of the Home Property record.

	Returns:
		dict with "warranties" list ordered by end_date asc.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)

	warranties = frappe.get_all(
		"Home Warranty",
		filters={"property": property},
		fields=[
			"name",
			"item",
			"warranty_type",
			"provider",
			"start_date",
			"end_date",
		],
		order_by="end_date asc",
	)

	for w in warranties:
		w["expiry_status"], w["days_remaining"] = _compute_expiry_status(w["end_date"])

		# Fetch item name for display
		w["item_name"] = frappe.db.get_value(
			"Home Item", w["item"], "item_name"
		)

	return {"warranties": warranties}


# ---------------------------------------------------------------------------
# Feature 10 — Claim management
# ---------------------------------------------------------------------------

_VALID_OUTCOMES = ("Pending", "Accepted", "Partial", "Rejected")


@frappe.whitelist()
def add_claim(
	warranty: str,
	claim_date: str,
	description: str,
	outcome: str = "Pending",
	amount_reimbursed: float = 0,
	notes: str = "",
) -> dict:
	"""Add a claim to a warranty record.

	Only Owner and Adult roles can add claims.

	Args:
		warranty: Name of the Home Warranty record.
		claim_date: Date the claim was submitted.
		description: What the claim is for.
		outcome: Pending / Accepted / Partial / Rejected.
		amount_reimbursed: Amount recovered (default 0).
		notes: Additional details.

	Returns:
		dict with warranty name and new claim idx.
	"""
	doc = frappe.get_doc("Home Warranty", warranty)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	if outcome not in _VALID_OUTCOMES:
		frappe.throw(
			_("Outcome must be one of: {0}").format(", ".join(_VALID_OUTCOMES))
		)

	row = doc.append("claims", {
		"claim_date": claim_date,
		"description": description,
		"outcome": outcome,
		"amount_reimbursed": amount_reimbursed,
		"notes": notes,
	})
	doc.save()

	return {
		"warranty": doc.name,
		"claim_idx": row.idx,
		"claim_name": row.name,
	}


@frappe.whitelist()
def update_claim(
	warranty: str,
	claim_idx: int,
	outcome: str | None = None,
	amount_reimbursed: float | None = None,
	notes: str | None = None,
) -> dict:
	"""Update an existing claim on a warranty.

	Only Owner and Adult roles can update claims.

	Args:
		warranty: Name of the Home Warranty record.
		claim_idx: idx of the claim row to update.
		outcome: New outcome (optional).
		amount_reimbursed: New amount (optional).
		notes: Updated notes (optional).

	Returns:
		dict with warranty name and updated claim_idx.
	"""
	doc = frappe.get_doc("Home Warranty", warranty)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	claim_idx = int(claim_idx)
	claim_row = None
	for row in doc.claims:
		if row.idx == claim_idx:
			claim_row = row
			break

	if not claim_row:
		frappe.throw(
			_("Claim with idx {0} not found on warranty {1}").format(
				claim_idx, warranty
			)
		)

	if outcome is not None:
		if outcome not in _VALID_OUTCOMES:
			frappe.throw(
				_("Outcome must be one of: {0}").format(", ".join(_VALID_OUTCOMES))
			)
		claim_row.outcome = outcome

	if amount_reimbursed is not None:
		claim_row.amount_reimbursed = amount_reimbursed

	if notes is not None:
		claim_row.notes = notes

	doc.save()

	return {"warranty": doc.name, "claim_idx": claim_idx}
