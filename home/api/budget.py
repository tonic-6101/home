# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Household budget overview API.

Provides endpoints for viewing, suggesting, and saving annual budget targets
per property. Actuals are always computed at read time from existing Home
records (maintenance, utility bills, insurance policies). No stored actuals —
the budget only holds user-set annual targets per category.
"""

import json

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role

DEFAULT_CATEGORIES = [
	"Maintenance & Repairs",
	"Utilities",
	"Insurance",
	"Supplies & Consumables",
	"Garden & Exterior",
	"Improvement Projects",
]


@frappe.whitelist()
def get_overview(property: str, year: int) -> dict:
	"""Return budget overview for a property and year.

	Each budget line includes the user-set annual target, actual spend
	computed from existing records, expected pace, and status indicator.
	Soft integration lines (Mesa, Rent) are appended when those apps
	are installed — silently omitted on failure.

	Args:
		property: Name of the Home Property record.
		year: Budget year (calendar year integer).

	Returns:
		dict with budget_name, year, lines, soft_lines, totals, pace.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	year = int(year)
	budget = _get_or_create_budget(property, year)
	actuals = _compute_actuals(property, year)
	pace = _compute_pace(year)

	lines = []
	for line in budget.lines:
		cat = line.category
		actual = actuals.get(cat, 0)
		target = line.annual_target or 0
		status = _compute_status(actual, target, pace)
		lines.append({
			"category": cat,
			"annual_target": target,
			"actual_spend": actual,
			"pace_expected": round((target / 12) * pace["months_elapsed"], 2) if target else None,
			"status": status,
			"notes": line.notes,
		})

	# Soft integrations — invisible when absent, silent on failure
	soft_lines = []
	soft_lines += _get_mesa_line(year)
	soft_lines += _get_rent_line(year)

	return {
		"budget_name": budget.name,
		"year": year,
		"lines": lines,
		"soft_lines": soft_lines,
		"totals": {
			"annual_target": sum(l["annual_target"] for l in lines),
			"actual_spend": sum(l["actual_spend"] for l in lines),
			"pace_expected": sum(l["pace_expected"] or 0 for l in lines),
		},
		"pace": pace,
	}


@frappe.whitelist()
def suggest_targets(property: str, year: int) -> dict:
	"""Return auto-suggested annual targets for the budget setup wizard.

	Suggestions are seeded from prior-year actuals. Maintenance uses the
	1% of purchase price rule (Fannie Mae / State Farm benchmark) when
	purchase price is available; otherwise falls back to last year's spend.

	Args:
		property: Name of the Home Property record.
		year: Budget year to suggest targets for.

	Returns:
		dict with suggestions keyed by category, each containing amount and basis.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	year = int(year)
	prior_year = year - 1
	actuals = _compute_actuals(property, prior_year)

	# 1% rule for maintenance
	purchase_price = doc.purchase_price or 0
	if purchase_price:
		maintenance_suggestion = round(purchase_price * 0.01, 0)
		maintenance_basis = "1% of property value"
	else:
		maintenance_suggestion = actuals.get("Maintenance & Repairs", 0)
		maintenance_basis = "last year's spend"

	# Insurance: use current active policy premiums (not prior year)
	insurance_rows = frappe.get_all(
		"Home Insurance Policy",
		filters={"property": property, "end_date": [">=", f"{year}-01-01"]},
		fields=["premium_annual"],
	)
	insurance_suggestion = sum((r.get("premium_annual") or 0) for r in insurance_rows)

	return {
		"suggestions": {
			"Maintenance & Repairs": {
				"amount": maintenance_suggestion,
				"basis": maintenance_basis,
			},
			"Utilities": {
				"amount": actuals.get("Utilities", 0),
				"basis": "last year's bills",
			},
			"Insurance": {
				"amount": insurance_suggestion,
				"basis": "active policy premiums",
			},
			"Supplies & Consumables": {
				"amount": 0,
				"basis": "no data",
			},
			"Garden & Exterior": {
				"amount": actuals.get("Garden & Exterior", 0),
				"basis": "last year's maintenance",
			},
			"Improvement Projects": {
				"amount": actuals.get("Improvement Projects", 0),
				"basis": "last year's maintenance",
			},
		}
	}


@frappe.whitelist()
def save_targets(property: str, year: int, targets: str | dict) -> dict:
	"""Create or update Home Budget for the given year with user-set targets.

	Args:
		property: Name of the Home Property record.
		year: Budget year.
		targets: dict mapping category name to annual target amount.

	Returns:
		dict with the budget record name.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	year = int(year)
	if isinstance(targets, str):
		targets = json.loads(targets)

	budget = _get_or_create_budget(property, year)
	budget.lines = []
	for category, amount in targets.items():
		budget.append("lines", {"category": category, "annual_target": amount})
	budget.save(ignore_permissions=False)

	return {"budget": budget.name}


@frappe.whitelist()
def get_category_detail(property: str, year: int, category: str) -> dict:
	"""Return drill-down detail for a single budget category.

	For maintenance-based categories, returns individual spend events.
	For utilities, returns individual bills. For insurance, returns
	active policies. Other categories return an empty list.

	Args:
		property: Name of the Home Property record.
		year: Budget year.
		category: Budget category name.

	Returns:
		dict with category, year, type (event/flowing), and rows.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	year = int(year)
	year_start = f"{year}-01-01"
	year_end = f"{year}-12-31"

	if category in ("Maintenance & Repairs", "Garden & Exterior", "Improvement Projects"):
		cat_filters = {
			"Maintenance & Repairs": [
				"Plumbing", "Electrical", "HVAC", "Roofing",
				"Painting & Decorating", "Pest Control",
				"Cleaning", "General Repair", "Other",
			],
			"Garden & Exterior": ["Garden & Landscaping"],
			"Improvement Projects": ["Renovation & Building"],
		}
		rows = frappe.get_all(
			"Home Maintenance",
			filters={
				"property": property,
				"status": "Completed",
				"completed_date": ["between", [year_start, year_end]],
				"category": ["in", cat_filters[category]],
			},
			fields=["name", "title", "category", "completed_date", "cost", "contractor"],
			order_by="completed_date asc",
		)
		return {"category": category, "year": year, "type": "event", "rows": rows}

	elif category == "Utilities":
		rows = frappe.get_all(
			"Home Utility Bill",
			filters={
				"property": property,
				"period_end": ["between", [year_start, year_end]],
			},
			fields=[
				"name", "bill_type", "amount", "period_start",
				"period_end", "paid",
			],
			order_by="period_end asc",
		)
		return {"category": category, "year": year, "type": "flowing", "rows": rows}

	elif category == "Insurance":
		rows = frappe.get_all(
			"Home Insurance Policy",
			filters={
				"property": property,
				"start_date": ["<=", year_end],
				"end_date": [">=", year_start],
			},
			fields=[
				"name", "policy_name", "policy_type", "provider",
				"premium_annual", "end_date", "auto_renews",
			],
		)
		return {"category": category, "year": year, "type": "event", "rows": rows}

	else:
		return {"category": category, "year": year, "type": "flowing", "rows": []}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_or_create_budget(property: str, year: int):
	"""Return existing Home Budget for property+year, or create one with defaults."""
	existing = frappe.get_all(
		"Home Budget",
		filters={"property": property, "budget_year": year},
		fields=["name"],
		limit=1,
	)
	if existing:
		return frappe.get_doc("Home Budget", existing[0].name)

	budget = frappe.new_doc("Home Budget")
	budget.property = property
	budget.budget_year = year
	# household populated by controller before_save
	_add_default_lines(budget)
	budget.insert(ignore_permissions=False)
	return budget


def _add_default_lines(budget) -> None:
	"""Add the six standard budget category lines with null targets."""
	for cat in DEFAULT_CATEGORIES:
		budget.append("lines", {"category": cat, "annual_target": None})


def _compute_actuals(property: str, year: int) -> dict:
	"""Aggregate actual spend per category from existing Home records.

	Sources:
	- Home Maintenance (completed, with cost) -> Maintenance, Garden, Improvement
	- Home Utility Bill (period_end in year) -> Utilities
	- Home Insurance Policy (active during year) -> Insurance
	- Supplies & Consumables has no data source in v1

	Returns:
		dict mapping category name to total spend amount.
	"""
	year_start = f"{year}-01-01"
	year_end = f"{year}-12-31"

	# Maintenance — all completed tasks with cost
	maintenance_rows = frappe.get_all(
		"Home Maintenance",
		filters={
			"property": property,
			"status": "Completed",
			"completed_date": ["between", [year_start, year_end]],
		},
		fields=["category", "cost"],
	)

	maintenance_total = 0
	garden_total = 0
	improvement_total = 0

	for row in maintenance_rows:
		cost = row.get("cost") or 0
		cat = row.get("category") or ""
		if cat == "Garden & Landscaping":
			garden_total += cost
		elif cat == "Renovation & Building":
			improvement_total += cost
		else:
			maintenance_total += cost

	# Utilities
	utility_rows = frappe.get_all(
		"Home Utility Bill",
		filters={
			"property": property,
			"period_end": ["between", [year_start, year_end]],
		},
		fields=["amount"],
	)
	utility_total = sum((r.get("amount") or 0) for r in utility_rows)

	# Insurance — annual premiums for policies active during year
	insurance_rows = frappe.get_all(
		"Home Insurance Policy",
		filters={
			"property": property,
			"start_date": ["<=", year_end],
			"end_date": [">=", year_start],
		},
		fields=["premium_annual"],
	)
	insurance_total = sum((r.get("premium_annual") or 0) for r in insurance_rows)

	return {
		"Maintenance & Repairs": maintenance_total,
		"Utilities": utility_total,
		"Insurance": insurance_total,
		"Supplies & Consumables": 0,  # no dedicated DocType — manual tracking only
		"Garden & Exterior": garden_total,
		"Improvement Projects": improvement_total,
	}


def _compute_pace(year: int) -> dict:
	"""Compute how far through the budget year we are.

	Returns months_elapsed (1-12 for current year), months_total,
	and pct_year_elapsed. Past years return 12; future years return 0.
	"""
	from frappe.utils import getdate, today as frappe_today

	today = getdate(frappe_today())
	if today.year > year:
		months_elapsed = 12
	elif today.year < year:
		months_elapsed = 0
	else:
		months_elapsed = today.month  # 1–12

	return {
		"months_elapsed": months_elapsed,
		"months_total": 12,
		"pct_year_elapsed": round(months_elapsed / 12 * 100, 1),
	}


def _compute_status(actual: float, target: float, pace: dict) -> str:
	"""Determine budget status for a category line.

	Returns one of: on_track, ahead_of_pace, over_budget, no_target.
	"""
	if not target:
		return "no_target"
	pace_expected = (target / 12) * pace["months_elapsed"]
	if actual > target:
		return "over_budget"
	elif actual > pace_expected:
		return "ahead_of_pace"
	else:
		return "on_track"


def _get_rent_line(year: int) -> list[dict]:
	"""Return Rent soft-integration line if Rent is installed.

	Calls ``rent.api.budget.get_monthly_total(year)`` which returns a dict
	with ``annual_total``, ``monthly_average``, ``currency``, and an
	optional ``components`` list. The line is read-only — no target-setting.
	Failures are silent.
	"""
	if "rent" not in frappe.get_installed_apps():
		return []
	try:
		rent_data = frappe.call("rent.api.budget.get_monthly_total", year=year)
		if not rent_data:
			return []
		if isinstance(rent_data, dict):
			return [{
				"source": "Rent",
				"label": "Housing Cost",
				"annual_total": rent_data.get("annual_total", 0),
				"monthly_average": rent_data.get("monthly_average", 0),
				"currency": rent_data.get("currency"),
				"components": rent_data.get("components", []),
				"read_only": True,
			}]
		# Backwards compat: if Rent returns a scalar (old API)
		return [{
			"source": "Rent",
			"label": "Housing Cost",
			"annual_total": float(rent_data),
			"monthly_average": round(float(rent_data) / 12, 2),
			"components": [],
			"read_only": True,
		}]
	except Exception:
		return []


def _get_mesa_line(year: int) -> list[dict]:
	"""Return Mesa soft-integration line if Mesa is installed.

	Same pattern as Rent — calls Mesa's budget endpoint. Failures are silent.
	"""
	if "mesa" not in frappe.get_installed_apps():
		return []
	try:
		mesa_data = frappe.call("mesa.api.budget.get_monthly_total", year=year)
		if not mesa_data:
			return []
		if isinstance(mesa_data, dict):
			return [{
				"source": "Mesa",
				"label": "Groceries",
				"annual_total": mesa_data.get("annual_total", 0),
				"monthly_average": mesa_data.get("monthly_average", 0),
				"currency": mesa_data.get("currency"),
				"components": mesa_data.get("components", []),
				"read_only": True,
			}]
		return [{
			"source": "Mesa",
			"label": "Groceries",
			"annual_total": float(mesa_data),
			"monthly_average": round(float(mesa_data) / 12, 2),
			"components": [],
			"read_only": True,
		}]
	except Exception:
		return []
