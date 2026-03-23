# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Home equity tracker API.

Provides endpoints for viewing current equity, updating estimated property
value, and recording equity snapshots. Only applicable to Owner-occupied
properties. All values are user-entered — no bank or valuation API integration.
"""

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role


@frappe.whitelist()
def get_equity(property: str) -> dict:
	"""Return equity data for an owner-occupied property.

	Computes equity (estimated value minus total mortgage balance), LTV ratio,
	value gain versus purchase price, and returns the snapshot history.

	Args:
		property: Name of the Home Property record.

	Returns:
		dict with applicable flag, equity figures, mortgages, and snapshots.
		If property is not Owner-occupied, returns {"applicable": False}.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	if doc.ownership_status not in ("Owner-occupied",):
		return {"applicable": False}

	estimated_value = doc.estimated_value or 0
	purchase_price = doc.purchase_price or 0

	mortgages = frappe.get_all(
		"Home Mortgage",
		filters={"property": property},
		fields=[
			"name", "mortgage_name", "lender", "outstanding_balance",
			"balance_date", "original_amount", "interest_rate",
			"monthly_payment", "term_end_date", "mortgage_type",
		],
		order_by="creation asc",
	)

	total_mortgage_balance = sum((m.get("outstanding_balance") or 0) for m in mortgages)
	equity_amount = estimated_value - total_mortgage_balance
	equity_pct = (equity_amount / estimated_value * 100) if estimated_value else None
	ltv = (total_mortgage_balance / estimated_value * 100) if estimated_value else None
	gain = estimated_value - purchase_price if purchase_price else None
	gain_pct = (gain / purchase_price * 100) if purchase_price else None

	snapshots = sorted(
		doc.equity_snapshots or [],
		key=lambda s: s.snapshot_date,
	)

	return {
		"applicable": True,
		"estimated_value": estimated_value,
		"estimated_value_date": doc.estimated_value_date,
		"purchase_price": purchase_price,
		"gain_vs_purchase": gain,
		"gain_pct": round(gain_pct, 1) if gain_pct is not None else None,
		"mortgages": mortgages,
		"total_mortgage_balance": total_mortgage_balance,
		"equity_amount": equity_amount,
		"equity_pct": round(equity_pct, 1) if equity_pct is not None else None,
		"ltv": round(ltv, 1) if ltv is not None else None,
		"snapshots": [s.as_dict() for s in snapshots],
		"has_estimated_value": bool(estimated_value),
	}


@frappe.whitelist()
def update_value(property: str, estimated_value: float, note: str = "") -> dict:
	"""Update the property's estimated market value and record a snapshot.

	Args:
		property: Name of the Home Property record.
		estimated_value: New estimated market value.
		note: Optional note for the snapshot (e.g. "After renovation").

	Returns:
		dict with the updated estimated_value and date.
	"""
	from frappe.utils import today

	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	doc.estimated_value = float(estimated_value)
	doc.estimated_value_date = today()
	_append_snapshot(doc, note=note)
	doc.save()

	return {"estimated_value": doc.estimated_value, "date": doc.estimated_value_date}


@frappe.whitelist()
def take_snapshot(property: str, note: str = "") -> dict:
	"""Record an equity snapshot without changing any values.

	Useful for marking a milestone or confirming current state without
	updating estimated value or mortgage balances.

	Args:
		property: Name of the Home Property record.
		note: Optional note for the snapshot.

	Returns:
		dict with the snapshot details.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	_append_snapshot(doc, note=note)
	doc.save()

	snapshot = doc.equity_snapshots[-1]
	return {
		"snapshot_date": snapshot.snapshot_date,
		"estimated_value": snapshot.estimated_value,
		"total_mortgage_balance": snapshot.total_mortgage_balance,
		"equity_amount": snapshot.equity_amount,
		"equity_pct": snapshot.equity_pct,
		"note": snapshot.note,
	}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _append_snapshot(doc, note: str = "") -> None:
	"""Append a current equity snapshot to the property's snapshot child table.

	Computes equity from the property's current estimated_value and the sum
	of all mortgage outstanding balances. Prunes the snapshot list to the
	60 most recent entries.
	"""
	from frappe.utils import today

	mortgages = frappe.get_all(
		"Home Mortgage",
		filters={"property": doc.name},
		fields=["outstanding_balance"],
	)
	total_balance = sum((m.get("outstanding_balance") or 0) for m in mortgages)
	value = doc.estimated_value or 0
	equity = value - total_balance
	pct = (equity / value * 100) if value else 0

	doc.append("equity_snapshots", {
		"snapshot_date": today(),
		"estimated_value": value,
		"total_mortgage_balance": total_balance,
		"equity_amount": equity,
		"equity_pct": round(pct, 1),
		"note": note,
	})

	# Prune to 60 most recent
	if len(doc.equity_snapshots) > 60:
		doc.equity_snapshots = sorted(
			doc.equity_snapshots, key=lambda s: s.snapshot_date
		)[-60:]
