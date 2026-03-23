# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Utility bill API.

Provides bill listing grouped by type with 12-month rolling averages,
cost spike flags, overdue detection, and a quick-action to mark bills
as paid.
"""

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role


@frappe.whitelist()
def get_bills(property: str) -> dict:
	"""Return utility bills for a property grouped by bill type.

	Each bill is annotated with ``cost_spike`` (amount > 150% of
	12-month average) and ``overdue`` (unpaid past due date) flags.

	Args:
		property: Name of the Home Property record.

	Returns:
		dict with ``bills`` (grouped by bill_type), ``averages``
		(per type), and ``total_monthly_average``.
	"""
	from frappe.utils import today, add_months

	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	bills = frappe.get_all(
		"Home Utility Bill",
		filters={"property": property},
		fields=[
			"name", "bill_type", "provider", "period_start", "period_end",
			"amount", "due_date", "paid", "paid_date", "document",
		],
		order_by="period_start desc",
	)

	# Compute 12-month average per bill type
	averages = {}
	for bill_type in {b["bill_type"] for b in bills}:
		avg = frappe.db.get_value(
			"Home Utility Bill",
			{
				"property": property,
				"bill_type": bill_type,
				"period_start": [">=", add_months(today(), -12)],
			},
			"avg(amount)",
		)
		averages[bill_type] = round(avg or 0, 2)

	_today = today()
	for b in bills:
		avg = averages.get(b["bill_type"], 0)
		b["cost_spike"] = bool(avg and b["amount"] > avg * 1.5)
		b["overdue"] = bool(not b["paid"] and b["due_date"] and b["due_date"] < _today)

	# Group by bill type
	grouped: dict[str, list] = {}
	for b in bills:
		grouped.setdefault(b["bill_type"], []).append(b)

	total_monthly_avg = sum(averages.values())

	# Build 12-month trend per bill type (Feature 27 — Utility Cost Trends)
	# Each trend entry has month label and amount for charting
	from frappe.utils import add_months, getdate

	trends: dict[str, list] = {}
	_today_date = getdate(_today)
	for bill_type, type_bills in grouped.items():
		monthly: dict[str, float] = {}
		for i in range(12):
			month_date = getdate(add_months(_today, -(11 - i)))
			key = month_date.strftime("%Y-%m")
			monthly[key] = 0

		for b in type_bills:
			if b.get("period_start"):
				bill_month = getdate(b["period_start"]).strftime("%Y-%m")
				if bill_month in monthly:
					monthly[bill_month] += float(b["amount"] or 0)

		trends[bill_type] = [
			{"month": k, "amount": round(v, 2)} for k, v in monthly.items()
		]

	return {
		"bills": grouped,
		"averages": averages,
		"trends": trends,
		"total_monthly_average": round(total_monthly_avg, 2),
	}


@frappe.whitelist()
def mark_paid(bill_name: str) -> dict:
	"""Quick-action to mark a utility bill as paid.

	Sets ``paid = 1`` and ``paid_date = today()`` on the bill record.

	Args:
		bill_name: Name of the Home Utility Bill record.

	Returns:
		dict with ``bill`` name and ``paid_date``.
	"""
	from frappe.utils import today

	bill = frappe.get_doc("Home Utility Bill", bill_name)
	require_household_access(bill.household)
	require_role(bill.household, "Adult")

	if bill.paid:
		return {"bill": bill_name, "paid_date": str(bill.paid_date), "already_paid": True}

	bill.paid = 1
	bill.paid_date = today()
	bill.save()

	return {"bill": bill_name, "paid_date": today(), "already_paid": False}


@frappe.whitelist()
def get_consumption_trends(property: str, year: int, utility_type: str) -> dict:
	"""Return monthly consumption breakdown for a utility type with YoY comparison.

	Separates price changes from consumption changes. Includes per-m²
	metric when ``area_sqm`` is set on the property.

	Args:
		property: Name of the Home Property record.
		year: Calendar year (e.g. 2025).
		utility_type: Bill type (Electricity, Gas, Water, etc.).

	Returns:
		dict with monthly breakdown, totals, YoY comparison, and per-m² stat.
	"""
	from collections import defaultdict

	from frappe.utils import flt, getdate

	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	year = int(year)

	# Current year bills with consumption data
	bills = frappe.get_all(
		"Home Utility Bill",
		filters={
			"property": property,
			"bill_type": utility_type,
			"period_start": ["between", [f"{year}-01-01", f"{year}-12-31"]],
			"consumption_amount": [">", 0],
		},
		fields=["period_start", "consumption_amount", "consumption_unit", "amount"],
		order_by="period_start asc",
	)

	# Prior year bills for YoY comparison
	prior_bills = frappe.get_all(
		"Home Utility Bill",
		filters={
			"property": property,
			"bill_type": utility_type,
			"period_start": ["between", [f"{year - 1}-01-01", f"{year - 1}-12-31"]],
			"consumption_amount": [">", 0],
		},
		fields=["consumption_amount", "amount"],
	)

	# Monthly breakdown
	by_month: dict[int, float] = defaultdict(float)
	for b in bills:
		month = getdate(b["period_start"]).month
		by_month[month] += flt(b["consumption_amount"])

	total_consumption = sum(flt(b["consumption_amount"]) for b in bills)
	total_cost = sum(flt(b["amount"]) for b in bills)
	prior_consumption = sum(flt(b["consumption_amount"]) for b in prior_bills)
	prior_cost = sum(flt(b["amount"]) for b in prior_bills)

	unit = bills[0]["consumption_unit"] if bills else None

	area_sqm = flt(frappe.db.get_value("Home Property", property, "area_sqm"))
	per_sqm = round(total_consumption / area_sqm, 1) if area_sqm and total_consumption else None

	# Count bills without consumption data
	total_bills = frappe.db.count(
		"Home Utility Bill",
		{
			"property": property,
			"bill_type": utility_type,
			"period_start": ["between", [f"{year}-01-01", f"{year}-12-31"]],
		},
	)
	bills_with_consumption = len(bills)
	bills_without_consumption = total_bills - bills_with_consumption

	return {
		"year": year,
		"utility_type": utility_type,
		"unit": unit,
		"monthly": [{"month": m, "consumption": round(by_month.get(m, 0), 2)} for m in range(1, 13)],
		"total_consumption": round(total_consumption, 2),
		"total_cost": round(total_cost, 2),
		"prior_consumption": round(prior_consumption, 2),
		"prior_cost": round(prior_cost, 2),
		"consumption_change_pct": _pct_change(prior_consumption, total_consumption),
		"cost_change_pct": _pct_change(prior_cost, total_cost),
		"per_sqm": per_sqm,
		"bills_without_consumption": bills_without_consumption,
	}


def _pct_change(prior: float, current: float) -> float | None:
	"""Compute percentage change from prior to current. None if no prior data."""
	if not prior:
		return None
	return round((current - prior) / prior * 100, 1)
