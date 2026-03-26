# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Home health score API (Feature 36).

Computes a property health score from 8 deduction factors.
Score = max(0, 100 - deductions). No data stored — always computed on demand.
"""

import frappe
from frappe import _
from frappe.utils import add_days, getdate, today

from home.api.permission import (
	get_household_role,
	require_household_access,
)
from home.api.property import _safe_count, _safe_get_all


def _get_band(score: int) -> dict:
	"""Return band label and colour for a score."""
	if score >= 90:
		return {"label": "Excellent", "colour": "green"}
	if score >= 75:
		return {"label": "Good", "colour": "green"}
	if score >= 50:
		return {"label": "Fair", "colour": "amber"}
	if score >= 25:
		return {"label": "Needs attention", "colour": "amber"}
	return {"label": "Poor", "colour": "red"}


def _count_deduction(count: int, per_item: int, cap: int) -> int:
	return min(count * per_item, cap)


@frappe.whitelist()
def get_health_score(property: str) -> dict:
	"""Compute the health score for a property.

	Returns score (0–100), band, colour, and factor breakdown with
	severity, action routes, and financial flags. Child role sees
	factor labels but no action links for financial factors.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)

	now = today()
	factors = []

	# 1. Overdue tasks: -5 per task, cap -30
	overdue_tasks = _safe_get_all(
		"Orga Task",
		filters={
			"home_property": property,
			"status": ["in", ["Open", "In Progress"]],
			"due_date": ["<", now],
			"home_maintenance_category": ["is", "set"],
		},
		fields=["name"],
	)
	overdue_count = len(overdue_tasks)
	d = _count_deduction(overdue_count, 5, 30)
	if overdue_count:
		factors.append({
			"key": "overdue_tasks",
			"label": _("{0} overdue task{1}").format(
				overdue_count, "s" if overdue_count != 1 else ""
			),
			"count": overdue_count,
			"deduction": d,
			"severity": "high",
			"action_route": f"/orga/my-tasks?home_property={property}",
			"financial": False,
		})

	# 2. Needs Repair appliances: -8 per appliance, cap -24
	needs_repair_list = _safe_get_all(
		"Home Item",
		filters={"property": property, "item_type": "Appliance", "status": "Needs Repair"},
		fields=["name"],
	)
	nr_count = len(needs_repair_list)
	d = _count_deduction(nr_count, 8, 24)
	if nr_count:
		factors.append({
			"key": "needs_repair",
			"label": _("{0} appliance{1} need{2} repair").format(
				nr_count,
				"s" if nr_count != 1 else "",
				"" if nr_count != 1 else "s",
			),
			"count": nr_count,
			"deduction": d,
			"severity": "high",
			"action_route": f"/home/property/{property}/items?filter=needs_repair",
			"financial": False,
		})

	# 3. Broken appliances: -10 per appliance, cap -20
	broken_list = _safe_get_all(
		"Home Item",
		filters={"property": property, "item_type": "Appliance", "status": "Broken"},
		fields=["name"],
	)
	broken_count = len(broken_list)
	d = _count_deduction(broken_count, 10, 20)
	if broken_count:
		factors.append({
			"key": "broken",
			"label": _("{0} broken appliance{1}").format(
				broken_count, "s" if broken_count != 1 else ""
			),
			"count": broken_count,
			"deduction": d,
			"severity": "high",
			"action_route": f"/home/property/{property}/items?filter=broken",
			"financial": False,
		})

	# 4. Past lifespan appliances: -4 per appliance, cap -20
	working_appliances = _safe_get_all(
		"Home Item",
		filters={
			"property": property,
			"item_type": "Appliance",
			"status": "Working",
			"purchase_date": ["is", "set"],
		},
		fields=["name", "category", "purchase_date"],
	)
	past_lifespan_count = 0
	for appl in working_appliances:
		if not appl.get("category"):
			continue
		lifespan_rows = frappe.get_all(
			"Home Item Category Lifespan",
			filters={"category": appl["category"]},
			fields=["average_lifespan_years"],
			limit=1,
		)
		if not lifespan_rows:
			continue
		expected_years = lifespan_rows[0]["average_lifespan_years"]
		age_days = (getdate(now) - getdate(appl["purchase_date"])).days
		if age_days > expected_years * 365:
			past_lifespan_count += 1

	d = _count_deduction(past_lifespan_count, 4, 20)
	if past_lifespan_count:
		factors.append({
			"key": "past_lifespan",
			"label": _("{0} appliance{1} past expected lifespan").format(
				past_lifespan_count, "s" if past_lifespan_count != 1 else ""
			),
			"count": past_lifespan_count,
			"deduction": d,
			"severity": "medium",
			"action_route": f"/home/property/{property}/items",
			"financial": False,
		})

	# 5. Expired warranties on active appliances: -5 per warranty, cap -15
	active_names = [a["name"] for a in working_appliances + needs_repair_list]
	expired_count = 0
	if active_names:
		expired_count = _safe_count(
			"Home Warranty",
			filters={
				"item": ["in", active_names],
				"end_date": ["<", now],
			},
		)
	d = _count_deduction(expired_count, 5, 15)
	if expired_count:
		factors.append({
			"key": "expired_warranties",
			"label": _("{0} expired warrant{1} on active appliances").format(
				expired_count, "ies" if expired_count != 1 else "y"
			),
			"count": expired_count,
			"deduction": d,
			"severity": "medium",
			"action_route": f"/home/property/{property}/warranties?filter=expired",
			"financial": True,
		})

	# 6. Warranties expiring within 30 days: -3 per warranty, cap -9
	expiring_count = 0
	if active_names:
		expiring_count = _safe_count(
			"Home Warranty",
			filters={
				"item": ["in", active_names],
				"end_date": ["between", [now, add_days(now, 30)]],
			},
		)
	d = _count_deduction(expiring_count, 3, 9)
	if expiring_count:
		factors.append({
			"key": "expiring_soon",
			"label": _("{0} warrant{1} expiring within 30 days").format(
				expiring_count, "ies" if expiring_count != 1 else "y"
			),
			"count": expiring_count,
			"deduction": d,
			"severity": "low",
			"action_route": f"/home/property/{property}/warranties?filter=expiring",
			"financial": True,
		})

	# 7. No emergency shutoff info: -5 flat
	has_emergency = any([
		prop.get("gas_shutoff_location"),
		prop.get("water_shutoff_location"),
		prop.get("electricity_shutoff_location"),
	])
	if not has_emergency:
		factors.append({
			"key": "no_emergency_info",
			"label": _("No emergency shutoff information recorded"),
			"count": 1,
			"deduction": 5,
			"severity": "low",
			"action_route": f"/home/property/{property}#emergency",
			"financial": False,
		})

	# 8. No insurance: -5 flat
	active_policies = _safe_count(
		"Home Insurance Policy",
		filters={"property": property, "end_date": [">=", now]},
	)
	if not active_policies:
		factors.append({
			"key": "no_insurance",
			"label": _("No active insurance policies"),
			"count": 1,
			"deduction": 5,
			"severity": "medium",
			"action_route": f"/home/property/{property}/insurance",
			"financial": True,
		})

	total_deduction = sum(f["deduction"] for f in factors)
	score = max(0, 100 - total_deduction)
	band = _get_band(score)

	# Sort by deduction size (largest first)
	factors.sort(key=lambda f: f["deduction"], reverse=True)

	# Strip action_route from financial factors for Child role
	role = get_household_role(prop.household)
	if role == "Child":
		for f in factors:
			if f.get("financial"):
				f.pop("action_route", None)

	return {
		"score": score,
		"band": band["label"],
		"colour": band["colour"],
		"total_deduction": total_deduction,
		"factors": factors,
	}
