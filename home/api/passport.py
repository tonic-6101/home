# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Digital property passport API (Feature 37).

Compiles a chronological timeline of property events (maintenance, item
installations, warranty records, room additions) for handover or personal
reference.  Excludes utility bills, budget, household members, and
mortgage history.
"""

import csv
import io

import frappe
from frappe import _
from frappe.utils import add_days, getdate, today
from frappe.utils.pdf import get_pdf

from home.api.permission import require_household_access, require_role


EVENT_TYPES = {
	"maintenance_completed",
	"appliance_installed",
	"appliance_disposed",
	"warranty_registered",
	"room_added",
}


def _resolve_period(period: str | None, start: str | None, end: str | None) -> tuple:
	"""Return (start_date, end_date) based on period shorthand or explicit dates."""
	now = getdate(today())

	if start and end:
		return getdate(start), getdate(end)

	if period == "5yr":
		return add_days(now, -5 * 365), now
	elif period == "10yr":
		return add_days(now, -10 * 365), now
	else:
		# "all" or default — no filtering
		return None, None


def _maintenance_events(property: str, start_date, end_date) -> list[dict]:
	"""Maintenance completed events."""
	filters = {
		"home_property": property,
		"status": "Completed",
		"completed_date": ["is", "set"],
	}
	if start_date and end_date:
		filters["completed_date"] = ["between", [str(start_date), str(end_date)]]

	rows = frappe.get_all(
		"Orga Task",
		filters=filters,
		fields=["name", "subject as title", "home_maintenance_category as category", "completed_date", "home_contractor as contractor", "actual_cost as cost"],
		order_by="completed_date asc",
	)
	return [
		{
			"event_type": "maintenance_completed",
			"date": str(r.completed_date),
			"label": r.title,
			"sub_label": r.contractor or "",
			"category": r.category,
			"cost": r.cost or 0,
			"source_doctype": "Orga Task",
			"source_name": r.name,
		}
		for r in rows
	]


def _item_events(property: str, start_date, end_date) -> list[dict]:
	"""Item installed and disposed events (appliance type only)."""
	rows = frappe.get_all(
		"Home Item",
		filters={"property": property, "item_type": "Appliance"},
		fields=[
			"name", "item_name", "brand", "model", "serial_number",
			"purchase_date", "purchase_price", "status", "modified",
		],
		order_by="purchase_date asc",
	)
	events = []
	for r in rows:
		# Item installed
		if r.purchase_date:
			date = str(r.purchase_date)
			in_range = True
			if start_date and date < str(start_date):
				in_range = False
			if end_date and date > str(end_date):
				in_range = False
			if in_range:
				events.append({
					"event_type": "appliance_installed",
					"date": date,
					"label": f"{r.item_name} installed",
					"sub_label": f"{r.brand or ''} {r.model or ''}".strip(),
					"serial_number": r.serial_number,
					"cost": r.purchase_price or 0,
					"source_doctype": "Home Item",
					"source_name": r.name,
				})

		# Item disposed
		if r.status == "Disposed":
			disposed_date = str(getdate(r.modified))
			in_range = True
			if start_date and disposed_date < str(start_date):
				in_range = False
			if end_date and disposed_date > str(end_date):
				in_range = False
			if in_range:
				events.append({
					"event_type": "appliance_disposed",
					"date": disposed_date,
					"label": f"{r.item_name} removed",
					"sub_label": "",
					"cost": 0,
					"source_doctype": "Home Item",
					"source_name": r.name,
				})

	return events


def _warranty_events(property: str, start_date, end_date) -> list[dict]:
	"""Warranty registered events."""
	filters = {"property": property}
	if start_date and end_date:
		filters["start_date"] = ["between", [str(start_date), str(end_date)]]

	rows = frappe.get_all(
		"Home Warranty",
		filters=filters,
		fields=["name", "item", "warranty_type", "provider", "start_date", "end_date"],
		order_by="start_date asc",
	)
	events = []
	for r in rows:
		if not r.start_date:
			continue
		item_name = ""
		if r.item:
			item_name = frappe.db.get_value("Home Item", r.item, "item_name") or ""
		events.append({
			"event_type": "warranty_registered",
			"date": str(r.start_date),
			"label": f"{r.warranty_type} warranty — {item_name}".strip(" —"),
			"sub_label": r.provider or "",
			"end_date": str(r.end_date) if r.end_date else "",
			"cost": 0,
			"source_doctype": "Home Warranty",
			"source_name": r.name,
		})
	return events


def _room_events(property: str, start_date, end_date) -> list[dict]:
	"""Room added events."""
	rows = frappe.get_all(
		"Home Room",
		filters={"property": property},
		fields=["name", "room_name", "room_type", "creation"],
		order_by="creation asc",
	)
	events = []
	for r in rows:
		date = str(r.creation)[:10]
		if start_date and date < str(start_date):
			continue
		if end_date and date > str(end_date):
			continue
		events.append({
			"event_type": "room_added",
			"date": date,
			"label": f"Room added: {r.room_name}",
			"sub_label": r.room_type or "",
			"cost": 0,
			"source_doctype": "Home Room",
			"source_name": r.name,
		})
	return events


def _build_timeline(property: str, start_date, end_date) -> list[dict]:
	"""Build a chronological list of passport events for a property."""
	events = []
	events += _maintenance_events(property, start_date, end_date)
	events += _item_events(property, start_date, end_date)
	events += _warranty_events(property, start_date, end_date)
	events += _room_events(property, start_date, end_date)

	events.sort(key=lambda e: e["date"])
	return events


def _current_state(property: str) -> dict:
	"""Build the current-state snapshot appended to the passport."""
	_today = today()

	items = frappe.get_all(
		"Home Item",
		filters={"property": property, "item_type": "Appliance", "status": ["in", ["Working", "Needs Repair"]]},
		fields=[
			"name", "item_name", "brand", "model", "serial_number",
			"purchase_date", "status",
		],
	)

	# Active warranties — filter to this property's items
	prop_item_names = {a["name"] for a in items}
	warranties = []
	if prop_item_names:
		warranties = frappe.get_all(
			"Home Warranty",
			filters={
				"item": ["in", list(prop_item_names)],
				"end_date": [">=", _today],
			},
			fields=["name", "warranty_type", "provider", "end_date", "item"],
		)

	insurance = frappe.get_all(
		"Home Insurance Policy",
		filters={"property": property, "end_date": [">=", _today]},
		fields=[
			"name", "policy_name", "policy_type", "provider",
			"policy_number", "coverage_amount", "end_date",
		],
	)

	prop = frappe.get_doc("Home Property", property)
	emergency = {
		"gas_shutoff_location": prop.get("gas_shutoff_location"),
		"water_shutoff_location": prop.get("water_shutoff_location"),
		"electricity_shutoff_location": prop.get("electricity_shutoff_location"),
		"evacuation_notes": prop.get("evacuation_notes"),
	}

	return {
		"items": items,
		"warranties": warranties,
		"insurance": insurance,
		"emergency": emergency,
	}


def _build_summary(events: list[dict], prop_doc) -> dict:
	"""Build summary statistics for the passport cover page."""
	maintenance = [e for e in events if e["event_type"] == "maintenance_completed"]
	installed = [e for e in events if e["event_type"] == "appliance_installed"]
	disposed = [e for e in events if e["event_type"] == "appliance_disposed"]
	warranties = [e for e in events if e["event_type"] == "warranty_registered"]

	return {
		"maintenance_count": len(maintenance),
		"appliances_installed": len(installed),
		"appliances_removed": len(disposed),
		"warranties_registered": len(warranties),
		"total_maintenance_spend": round(sum(e["cost"] for e in maintenance), 2),
		"total_appliance_spend": round(sum(e["cost"] for e in installed), 2),
	}


@frappe.whitelist()
def get_passport(
	property: str,
	period: str = "all",
	start: str | None = None,
	end: str | None = None,
) -> dict:
	"""Get the digital property passport — timeline, current state, and summary.

	Args:
		property: Name of the Home Property.
		period: "all" (default), "5yr", "10yr", or omit if using start/end.
		start: Custom start date (ISO format).
		end: Custom end date (ISO format).

	Returns:
		dict with property info, events list, current_state, and summary.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	start_date, end_date = _resolve_period(period, start, end)
	events = _build_timeline(property, start_date, end_date)
	current_state = _current_state(property)
	summary = _build_summary(events, prop)

	return {
		"property": prop.name,
		"property_name": prop.property_name,
		"property_type": prop.property_type,
		"address": ", ".join(
			filter(None, [prop.address_line1, prop.address_line2, prop.postal_code, prop.city])
		),
		"purchase_date": str(prop.purchase_date) if prop.get("purchase_date") else None,
		"purchase_price": prop.get("purchase_price"),
		"area_sqm": prop.get("area_sqm"),
		"period": period if not (start and end) else f"{start} to {end}",
		"generated_date": today(),
		"generated_by": frappe.session.user,
		"event_count": len(events),
		"events": events,
		"current_state": current_state,
		"summary": summary,
	}


@frappe.whitelist()
def export_passport_pdf(
	property: str,
	period: str = "all",
	start: str | None = None,
	end: str | None = None,
) -> None:
	"""Export the property passport as a PDF download.

	Args:
		property: Name of the Home Property.
		period: "all" (default), "5yr", "10yr".
		start: Custom start date (ISO format).
		end: Custom end date (ISO format).
	"""
	data = get_passport(property, period, start, end)

	html = frappe.render_template(
		"home/templates/passport.html",
		{"data": data, "_": _},
	)

	pdf = get_pdf(html)

	if start and end:
		filename = f"property-passport-{start}-to-{end}.pdf"
	else:
		filename = "property-passport.pdf"

	frappe.response["type"] = "download"
	frappe.response["filename"] = filename
	frappe.response["filecontent"] = pdf
	frappe.response["content_type"] = "application/pdf"


@frappe.whitelist()
def export_passport_csv(
	property: str,
	period: str = "all",
	start: str | None = None,
	end: str | None = None,
) -> None:
	"""Export the property passport as a CSV download.

	Args:
		property: Name of the Home Property.
		period: "all" (default), "5yr", "10yr".
		start: Custom start date (ISO format).
		end: Custom end date (ISO format).
	"""
	data = get_passport(property, period, start, end)

	output = io.StringIO()
	writer = csv.DictWriter(
		output,
		fieldnames=["date", "event_type", "label", "sub_label", "cost"],
	)
	writer.writeheader()
	for e in data["events"]:
		writer.writerow({
			"date": e["date"],
			"event_type": e["event_type"],
			"label": e["label"],
			"sub_label": e.get("sub_label", ""),
			"cost": e.get("cost") or "",
		})

	if start and end:
		filename = f"property-passport-{start}-to-{end}.csv"
	else:
		filename = "property-passport.csv"

	frappe.response["type"] = "download"
	frappe.response["filename"] = filename
	frappe.response["filecontent"] = "\ufeff" + output.getvalue()
	frappe.response["content_type"] = "text/csv"
