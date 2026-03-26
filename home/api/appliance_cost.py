# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Item Lifetime Cost API (Feature 24).

Computes lifetime cost metrics for items (appliances) — purchase price plus
cumulative maintenance — and projects future spend based on observed
maintenance rate and remaining expected lifespan.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, today

from home.api.permission import (
	get_household_role,
	require_household_access,
	require_role,
)


def _compute_item_cost(doc) -> dict:
	"""Compute lifetime cost metrics for a single item document.

	Args:
		doc: Home Item document (already fetched).

	Returns:
		dict with all computed cost fields.
	"""
	purchase_price = flt(doc.purchase_price)

	# --- Maintenance totals ---
	maintenance_records = frappe.get_all(
		"Orga Task",
		filters={
			"home_item": doc.name,
			"status": "Completed",
		},
		fields=["name", "subject as title", "actual_cost as cost", "completed_date"],
		order_by="completed_date asc",
	)

	maintenance_total = sum(flt(r.cost) for r in maintenance_records)
	lifetime_cost = purchase_price + maintenance_total

	# --- Age ---
	age_years = None
	if doc.purchase_date:
		delta = getdate(today()) - getdate(doc.purchase_date)
		age_years = round(delta.days / 365.25, 2)

	# --- Cost per year ---
	cost_per_year = None
	if age_years is not None and age_years >= 0.5:
		cost_per_year = round(lifetime_cost / age_years, 2)

	# --- Remaining years & projection ---
	expected_lifespan = flt(getattr(doc, "expected_lifespan_years", None))
	remaining_years = None
	projected_total = None
	past_lifespan = False

	if expected_lifespan > 0 and age_years is not None:
		remaining_years = max(0, round(expected_lifespan - age_years, 2))
		past_lifespan = age_years > expected_lifespan

	if remaining_years is not None and remaining_years > 0 and cost_per_year is not None:
		projected_total = round(lifetime_cost + (cost_per_year * remaining_years), 2)

	# --- Maintenance share ---
	maintenance_share = 0
	if lifetime_cost > 0:
		maintenance_share = round(maintenance_total / lifetime_cost * 100, 1)

	high_maintenance_note = maintenance_share >= 25

	# --- Breakdown ---
	maintenance_breakdown = [
		{
			"name": r.name,
			"title": r.title,
			"cost": flt(r.cost),
			"completed_date": r.completed_date,
		}
		for r in maintenance_records
	]

	return {
		"item": doc.name,
		"item_name": getattr(doc, "item_name", None),
		"status": doc.status,
		"purchase_price": purchase_price,
		"purchase_price_recorded": bool(doc.purchase_price),
		"purchase_date": doc.purchase_date,
		"maintenance_total": maintenance_total,
		"maintenance_count": len(maintenance_records),
		"lifetime_cost": lifetime_cost,
		"age_years": age_years,
		"cost_per_year": cost_per_year,
		"expected_lifespan_years": expected_lifespan or None,
		"remaining_years": remaining_years,
		"projected_total": projected_total,
		"past_lifespan": past_lifespan,
		"maintenance_share": maintenance_share,
		"high_maintenance_note": high_maintenance_note,
		"maintenance_breakdown": maintenance_breakdown,
	}


@frappe.whitelist()
def get_item_cost(item: str) -> dict:
	"""Compute lifetime cost metrics for a single item.

	Child role sees no cost data — returns a stub response.
	"""
	doc = frappe.get_doc("Home Item", item)
	require_household_access(doc.household)

	role = get_household_role(doc.household)
	if role == "Child":
		return {"access": "read_only", "cost_visible": False}

	return _compute_item_cost(doc)


@frappe.whitelist()
def get_property_item_costs(property: str) -> dict:
	"""Return cost metrics for all items (appliances) in a property.

	Adult or Owner only. Sorted by lifetime_cost descending.
	Active and disposed items separated; totals provided.
	"""
	prop_doc = frappe.get_doc("Home Property", property)
	require_household_access(prop_doc.household)
	require_role(prop_doc.household, "Adult")

	items = frappe.get_all(
		"Home Item",
		filters={"property": property, "item_type": "Appliance"},
		fields=["name", "status"],
	)

	active = []
	disposed = []
	for appl in items:
		doc = frappe.get_doc("Home Item", appl["name"])
		cost = _compute_item_cost(doc)
		if appl["status"] == "Disposed":
			disposed.append(cost)
		else:
			active.append(cost)

	active.sort(key=lambda r: r["lifetime_cost"], reverse=True)
	disposed.sort(key=lambda r: r["lifetime_cost"], reverse=True)

	# Totals across active appliances only (disposed excluded by default)
	total_purchase = sum(r["purchase_price"] for r in active)
	total_maintenance = sum(r["maintenance_total"] for r in active)
	total_lifetime = sum(r["lifetime_cost"] for r in active)

	return {
		"items": active,
		"disposed": disposed,
		"totals": {
			"purchase": total_purchase,
			"maintenance": total_maintenance,
			"lifetime": total_lifetime,
		},
	}
