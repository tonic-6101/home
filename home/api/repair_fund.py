# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Repair Fund Calculator API (Feature 21).

Computes a recommended annual repair fund target for a property based on
its age and value, then compares against actual year-to-date maintenance
spend to show whether the household is on track.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, today

from home.api.permission import require_household_access, require_role


def _property_age_years(doc) -> float | None:
	"""Return age in years from purchase_date or move_in_date, or None."""
	ref_date = doc.purchase_date or doc.get("move_in_date")
	if not ref_date:
		return None
	delta = getdate(today()) - getdate(ref_date)
	return delta.days / 365.25


def _select_rate(age_years: float) -> float:
	"""Auto-select repair fund rate based on property age."""
	if age_years < 10:
		return 0.01
	elif age_years <= 20:
		return 0.015
	else:
		return 0.02


RATE_OVERRIDE_MAP = {
	"1%": 0.01,
	"1.5%": 0.015,
	"2%": 0.02,
}


@frappe.whitelist()
def get_repair_fund(property: str) -> dict:
	"""Compute the repair fund recommendation for a property.

	Uses the 1/1.5/2% rule based on property age, with optional user
	override.  Falls back to area-based estimate if no purchase_price.

	Args:
		property: Name of the Home Property record.

	Returns:
		dict with rate, annual_target, monthly_target, ytd_actual,
		expected_pace, status, shortfall, and basis.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	null_result = {
		"has_data": False,
		"rate": None,
		"rate_override": None,
		"annual_target": None,
		"monthly_target": None,
		"ytd_actual": None,
		"expected_pace": None,
		"status": None,
		"shortfall": 0,
		"surplus": 0,
		"basis": None,
		"confidence": None,
		"months_elapsed": None,
		"current_year": None,
		"message": None,
	}

	# --- Age & rate ---
	age_years = _property_age_years(doc)
	if age_years is None and not flt(doc.purchase_price) and not flt(getattr(doc, "area_sqm", None)):
		null_result["message"] = _("Add your property's purchase price to get a recommendation.")
		return null_result

	# Use default rate if age unknown
	if age_years is None:
		rate = 0.015
		rate_basis = _("default (age unknown)")
	else:
		rate = _select_rate(age_years)
		rate_basis = _("{0} (property {1} years old)").format(
			_pct(rate),
			int(age_years),
		)

	# Check for user override
	override = getattr(doc, "repair_fund_rate_override", None) or "Auto"
	if override != "Auto" and override in RATE_OVERRIDE_MAP:
		rate = RATE_OVERRIDE_MAP[override]
		rate_basis = _("manual override ({0})").format(override)

	# --- Annual target ---
	basis = None
	annual_target = None
	confidence = None

	purchase_price = flt(getattr(doc, "purchase_price", None))
	area_sqm = flt(getattr(doc, "area_sqm", None))

	if purchase_price > 0:
		annual_target = purchase_price * rate
		basis = "purchase_price"
		confidence = "high"
	elif area_sqm > 0:
		annual_target = area_sqm * 1000 * rate
		basis = "area_estimate"
		confidence = "low"
	else:
		null_result["message"] = _(
			"Add your property's purchase price to get a recommendation."
		)
		return null_result

	monthly_target = annual_target / 12

	# --- YTD actuals ---
	current_year = getdate(today()).year
	year_start = f"{current_year}-01-01"
	year_end = f"{current_year}-12-31"

	ytd_actual = flt(
		frappe.db.sql(
			"""
			SELECT COALESCE(SUM(actual_cost), 0)
			FROM `tabOrga Task`
			WHERE home_property = %s
			  AND status = 'Completed'
			  AND completed_date BETWEEN %s AND %s
			""",
			(property, year_start, year_end),
		)[0][0]
	)

	# --- Pace & status ---
	months_elapsed = getdate(today()).month
	expected_pace = (annual_target / 12) * months_elapsed

	if ytd_actual >= expected_pace:
		status = "on_track"
		shortfall = 0
		surplus = round(ytd_actual - expected_pace, 2)
	else:
		status = "behind"
		shortfall = round(expected_pace - ytd_actual, 2)
		surplus = 0

	return {
		"has_data": True,
		"rate": rate,
		"rate_override": override,
		"rate_basis": rate_basis,
		"annual_target": round(annual_target, 2),
		"monthly_target": round(monthly_target, 2),
		"ytd_actual": ytd_actual,
		"expected_pace": round(expected_pace, 2),
		"status": status,
		"shortfall": shortfall,
		"surplus": surplus,
		"basis": basis,
		"confidence": confidence,
		"months_elapsed": months_elapsed,
		"current_year": current_year,
		"message": None,
	}


@frappe.whitelist()
def set_repair_fund_rate(property: str, rate_override: str) -> dict:
	"""Persist the user's rate override selection.

	Args:
		property: Name of the Home Property record.
		rate_override: One of 'Auto', '1%', '1.5%', '2%'.

	Returns:
		dict with the saved rate_override value.
	"""
	valid = {"Auto", "1%", "1.5%", "2%"}
	if rate_override not in valid:
		frappe.throw(_("Invalid rate. Choose Auto, 1%, 1.5%, or 2%."))

	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	doc.repair_fund_rate_override = rate_override
	doc.save(ignore_permissions=True)
	return {"rate_override": rate_override}


def _pct(rate: float) -> str:
	return f"{rate * 100:g}%"
