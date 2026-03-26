# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Annual Home Cost Report API (Feature 23).

Aggregates all property-related costs for a given calendar year from
maintenance, utility bills, insurance policies, item purchases,
and purchase returns (refunds). Provides structured
data, PDF export, and CSV export.
"""

import csv
import io
from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt, getdate, today

from home.api.permission import require_household_access, require_role


# ---------------------------------------------------------------------------
# Data collectors — one per source DocType
# ---------------------------------------------------------------------------


def _collect_maintenance_rows(property: str, year: int) -> list[dict]:
	"""Completed Orga Tasks with maintenance category and cost in the given year."""
	records = frappe.get_all(
		"Orga Task",
		filters={
			"home_property": property,
			"status": "Completed",
			"completed_date": ["between", [f"{year}-01-01", f"{year}-12-31"]],
			"home_maintenance_category": ["is", "set"],
		},
		fields=[
			"name", "subject as title", "home_maintenance_category as category",
			"actual_cost as cost", "home_room as room",
			"completed_date", "home_contractor as contractor", "home_item as item",
		],
	)
	return [
		{
			"source_doctype": "Orga Task",
			"source_name": r.name,
			"description": r.title,
			"category": _("Maintenance & Repairs"),
			"subcategory": r.category or _("Uncategorised"),
			"amount": flt(r.cost),
			"room": r.room,
			"item": r.item,
			"date": r.completed_date,
		}
		for r in records
		if flt(r.cost) > 0
	]


def _collect_utility_rows(property: str, year: int) -> list[dict]:
	"""Utility bills whose period_end falls in the given year."""
	records = frappe.get_all(
		"Home Utility Bill",
		filters={
			"property": property,
			"period_end": ["between", [f"{year}-01-01", f"{year}-12-31"]],
		},
		fields=["name", "bill_type", "amount", "provider", "period_start", "period_end"],
	)
	return [
		{
			"source_doctype": "Home Utility Bill",
			"source_name": r.name,
			"description": r.provider or r.bill_type,
			"category": _("Utilities"),
			"subcategory": r.bill_type or _("Utility"),
			"amount": flt(r.amount),
			"room": None,
			"item": None,
			"date": r.period_end,
		}
		for r in records
		if flt(r.amount) > 0
	]


def _collect_insurance_rows(property: str, year: int) -> list[dict]:
	"""Insurance policies whose end_date (renewal) falls in the given year."""
	records = frappe.get_all(
		"Home Insurance Policy",
		filters={
			"property": property,
			"end_date": ["between", [f"{year}-01-01", f"{year}-12-31"]],
		},
		fields=["name", "policy_name", "policy_type", "provider", "premium_annual", "end_date"],
	)
	return [
		{
			"source_doctype": "Home Insurance Policy",
			"source_name": r.name,
			"description": r.policy_name or r.provider,
			"category": _("Insurance"),
			"subcategory": r.policy_type or _("Insurance"),
			"amount": flt(r.premium_annual),
			"room": None,
			"item": None,
			"date": r.end_date,
		}
		for r in records
		if flt(r.premium_annual) > 0
	]


def _collect_item_rows(property: str, year: int) -> list[dict]:
	"""Items (appliances and possessions) purchased in the given year."""
	records = frappe.get_all(
		"Home Item",
		filters={
			"property": property,
			"purchase_date": ["between", [f"{year}-01-01", f"{year}-12-31"]],
		},
		fields=["name", "item_name", "item_type", "category", "brand", "model", "room", "purchase_date", "purchase_price"],
	)
	rows = []
	for r in records:
		if flt(r.purchase_price) <= 0:
			continue
		if r.item_type == "Appliance":
			rows.append({
				"source_doctype": "Home Item",
				"source_name": r.name,
				"description": r.item_name,
				"category": _("Appliance Purchases"),
				"subcategory": _("Appliance Purchase"),
				"amount": flt(r.purchase_price),
				"room": r.room,
				"item": r.name,
				"date": r.purchase_date,
			})
		else:
			rows.append({
				"source_doctype": "Home Item",
				"source_name": r.name,
				"description": r.item_name,
				"category": _("Possession Purchases"),
				"subcategory": r.category or _("Possession"),
				"amount": flt(r.purchase_price),
				"room": r.room,
				"item": None,
				"date": r.purchase_date,
			})
	return rows


def _collect_refund_rows(property: str, year: int) -> list[dict]:
	"""Purchase returns (refunds received) in the given year."""
	records = frappe.get_all(
		"Home Purchase Return",
		filters={
			"property": property,
			"refund_status": "Received",
			"refund_received_date": ["between", [f"{year}-01-01", f"{year}-12-31"]],
		},
		fields=["name", "item_description", "refund_amount_received", "refund_received_date"],
	)
	return [
		{
			"source_doctype": "Home Purchase Return",
			"source_name": r.name,
			"description": r.item_description,
			"category": _("Refunds Received"),
			"subcategory": _("Refund"),
			"amount": -flt(r.refund_amount_received),
			"room": None,
			"item": None,
			"date": r.refund_received_date,
		}
		for r in records
		if flt(r.refund_amount_received) > 0
	]


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def _aggregate_by_key(rows: list[dict], key: str) -> list[dict]:
	"""Group rows by a key and compute amount + share_pct."""
	totals: dict[str, float] = defaultdict(float)
	for row in rows:
		group = row.get(key) or _("Unassigned")
		totals[group] += flt(row["amount"])

	grand_total = sum(abs(v) for v in totals.values())
	result = []
	for group, amount in sorted(totals.items(), key=lambda x: -x[1]):
		result.append({
			key: group,
			"amount": round(amount, 2),
			"share_pct": round((abs(amount) / grand_total * 100) if grand_total else 0, 1),
		})
	return result


def _aggregate_by_month(rows: list[dict]) -> list[dict]:
	"""Group rows by calendar month (1-12)."""
	monthly: dict[int, float] = defaultdict(float)
	for row in rows:
		if row.get("date"):
			month = getdate(row["date"]).month
			monthly[month] += flt(row["amount"])

	return [
		{"month": m, "amount": round(monthly.get(m, 0), 2)}
		for m in range(1, 13)
	]


def _aggregate_by_item(rows: list[dict]) -> dict:
	"""Group maintenance and purchase rows by item."""
	result: dict[str, dict] = defaultdict(
		lambda: {"item_name": None, "purchase": 0, "maintenance": [], "maintenance_total": 0}
	)

	for row in rows:
		item_key = row.get("item")
		if not item_key:
			if row["source_doctype"] == "Orga Task":
				item_key = "__none__"
			else:
				continue

		entry = result[item_key]

		if row["source_doctype"] == "Home Item":
			entry["item_name"] = row["description"]
			entry["purchase"] = row["amount"]
		elif row["source_doctype"] == "Orga Task":
			if not entry["item_name"] and item_key != "__none__":
				# Fetch item name if not already set from purchase row
				entry["item_name"] = frappe.db.get_value(
					"Home Item", item_key, "item_name"
				) or item_key
			entry["maintenance"].append({
				"title": row["description"],
				"date": row["date"],
				"cost": row["amount"],
			})
			entry["maintenance_total"] += row["amount"]

	if "__none__" in result:
		result["__none__"]["item_name"] = _("No item link")

	for data in result.values():
		data["total"] = round(data["purchase"] + data["maintenance_total"], 2)

	return dict(result)


# ---------------------------------------------------------------------------
# Main API
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_cost_report(property: str, year: int) -> dict:
	"""Aggregate all costs for a property in a given calendar year.

	Collects from maintenance, utility bills, insurance, item
	purchases, and refunds.

	Args:
		property: Name of the Home Property record.
		year: Calendar year (integer).

	Returns:
		dict with total_spend, by_category, by_room, by_item,
		by_month, is_partial_year, record_count, and rows.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	year = int(year)

	# Collect all cost rows
	rows = []
	rows.extend(_collect_maintenance_rows(property, year))
	rows.extend(_collect_utility_rows(property, year))
	rows.extend(_collect_insurance_rows(property, year))
	rows.extend(_collect_item_rows(property, year))
	rows.extend(_collect_refund_rows(property, year))

	total_spend = round(sum(flt(r["amount"]) for r in rows), 2)
	current_year = getdate(today()).year

	return {
		"property": property,
		"year": year,
		"total_spend": total_spend,
		"by_category": _aggregate_by_key(rows, "category"),
		"by_room": _aggregate_by_key(
			[r for r in rows if r["source_doctype"] in ("Orga Task", "Home Item")],
			"room",
		),
		"by_item": _aggregate_by_item(rows),
		"by_month": _aggregate_by_month(rows),
		"is_partial_year": year == current_year,
		"record_count": len(rows),
		"rows": rows,
	}


# ---------------------------------------------------------------------------
# PDF export
# ---------------------------------------------------------------------------


def _filter_by_categories(report: dict, include: str | None) -> dict:
	"""Filter report rows to only included categories.

	Args:
		report: Full report dict from get_cost_report.
		include: JSON-encoded list of category names, or None/"all" for no filter.

	Returns:
		Filtered report dict (mutated copy).
	"""
	if not include or include == "all":
		return report

	import json

	try:
		include_list = json.loads(include) if isinstance(include, str) else include
	except (json.JSONDecodeError, TypeError):
		return report

	report["rows"] = [r for r in report["rows"] if r.get("category") in include_list]
	report["total_spend"] = round(sum(flt(r["amount"]) for r in report["rows"]), 2)
	report["by_category"] = [c for c in report["by_category"] if c.get("category") in include_list]
	report["record_count"] = len(report["rows"])
	return report


@frappe.whitelist()
def export_pdf(property: str, year: int, include: str | None = None) -> None:
	"""Generate and download a PDF cost report.

	Args:
		property: Name of the Home Property record.
		year: Calendar year (integer).
		include: Optional JSON list of categories to include (default: all).
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	report = _filter_by_categories(get_cost_report(property, int(year)), include)
	html = _render_report_html(doc, report)
	pdf_bytes = frappe.utils.pdf.get_pdf(html)

	partial = "-partial" if report["is_partial_year"] else ""
	filename = f"home-cost-report-{year}{partial}.pdf"
	frappe.local.response.filename = filename
	frappe.local.response.filecontent = pdf_bytes
	frappe.local.response.type = "download"


def _render_report_html(doc, report: dict) -> str:
	"""Render the cost report as HTML for PDF generation."""
	context = {
		"property_name": doc.property_name,
		"address": ", ".join(filter(None, [doc.address_line1, doc.city])),
		"year": report["year"],
		"is_partial": report["is_partial_year"],
		"generated_date": today(),
		"generated_by": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
		"total_spend": report["total_spend"],
		"record_count": report["record_count"],
		"by_category": report["by_category"],
		"by_room": report["by_room"],
		"by_item": report["by_item"],
		"rows": report["rows"],
	}

	html = frappe.render_template(
		"home/templates/cost_report.html",
		context,
	)
	return html


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------


@frappe.whitelist()
def export_csv(property: str, year: int, include: str | None = None) -> None:
	"""Generate and download a CSV cost report.

	Args:
		property: Name of the Home Property record.
		year: Calendar year (integer).
		include: Optional JSON list of categories to include (default: all).
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	report = _filter_by_categories(get_cost_report(property, int(year)), include)

	output = io.StringIO()
	writer = csv.DictWriter(output, fieldnames=[
		"date", "type", "category", "description", "room",
		"item", "amount",
	])
	writer.writeheader()

	for row in report["rows"]:
		writer.writerow({
			"date": row.get("date", ""),
			"type": row.get("source_doctype", ""),
			"category": row.get("category", ""),
			"description": row.get("description", ""),
			"room": row.get("room", ""),
			"item": row.get("item", ""),
			"amount": row.get("amount", 0),
		})

	partial = "-partial" if report["is_partial_year"] else ""
	filename = f"home-cost-report-{year}{partial}.csv"
	frappe.local.response.filename = filename
	frappe.local.response.filecontent = "\ufeff" + output.getvalue()
	frappe.local.response.type = "download"


# Keep backward-compatible alias
export_cost_report_csv = export_csv
