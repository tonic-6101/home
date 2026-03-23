# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Insurance inventory export API (Feature 19b).

Provides inventory data formatted for insurance documentation — list view,
PDF grouped by category, and CSV with UTF-8 BOM for spreadsheet compatibility.
Hidden from Child role entirely.
"""

import csv
import io

import frappe
from frappe import _
from frappe.utils import today
from frappe.utils.pdf import get_pdf

from home.api.permission import require_household_access, require_role


EXPORT_FIELDS = [
	"name",
	"item_name",
	"category",
	"brand",
	"model",
	"serial_number",
	"purchase_date",
	"purchase_price",
	"estimated_value",
	"condition",
	"photo",
	"insured",
	"room",
]


def _build_filters(property: str, insured_only: bool, min_value: float | None) -> dict:
	"""Build query filters for insurance inventory."""
	filters = {"property": property, "item_type": "Possession"}

	if insured_only:
		filters["insured"] = 1

	if min_value is not None and min_value > 0:
		filters["estimated_value"] = [">=", min_value]

	return filters


def _fetch_items(property: str, insured_only: bool, min_value: float | None) -> list[dict]:
	"""Fetch inventory items matching the insurance export criteria."""
	filters = _build_filters(property, insured_only, min_value)

	items = frappe.get_all(
		"Home Item",
		filters=filters,
		fields=EXPORT_FIELDS,
		order_by="category asc, item_name asc",
	)

	# Resolve room name for display
	for item in items:
		if item.get("room"):
			item["room_name"] = frappe.db.get_value("Home Room", item["room"], "room_name") or ""
		else:
			item["room_name"] = ""
		if item.get("purchase_date"):
			item["purchase_date"] = str(item["purchase_date"])

	return items


def _group_by_category(items: list[dict]) -> dict[str, list[dict]]:
	"""Group items by category for PDF output."""
	groups: dict[str, list[dict]] = {}
	for item in items:
		cat = item.get("category") or _("Uncategorized")
		groups.setdefault(cat, []).append(item)
	return groups


@frappe.whitelist()
def get_insurance_inventory(
	property: str,
	insured_only: bool = False,
	min_value: float | None = None,
) -> dict:
	"""Get inventory items formatted for insurance documentation.

	Args:
		property: Name of the Home Property.
		insured_only: If True, return only items marked as insured.
		min_value: Minimum estimated_value filter.

	Returns:
		dict with items list, total count, and total estimated value.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	# Convert string booleans from web requests
	if isinstance(insured_only, str):
		insured_only = insured_only.lower() in ("true", "1", "yes")
	if isinstance(min_value, str):
		min_value = float(min_value) if min_value else None

	items = _fetch_items(property, insured_only, min_value)

	total_value = sum(item.get("estimated_value") or 0 for item in items)
	total_purchase = sum(item.get("purchase_price") or 0 for item in items)

	return {
		"property": prop.name,
		"property_name": prop.property_name,
		"items": items,
		"count": len(items),
		"total_estimated_value": total_value,
		"total_purchase_price": total_purchase,
	}


@frappe.whitelist()
def export_insurance_pdf(
	property: str,
	insured_only: bool = False,
	min_value: float | None = None,
) -> None:
	"""Export insurance inventory as a PDF grouped by category.

	Args:
		property: Name of the Home Property.
		insured_only: If True, include only items marked as insured.
		min_value: Minimum estimated_value filter.
	"""
	data = get_insurance_inventory(property, insured_only, min_value)
	data["groups"] = _group_by_category(data["items"])

	html = frappe.render_template(
		"home/templates/insurance_inventory.html",
		{"data": data, "_": _},
	)

	pdf = get_pdf(html)

	filename = f"Insurance_Inventory_{data['property_name']}_{today()}.pdf"
	frappe.response["type"] = "download"
	frappe.response["filename"] = filename
	frappe.response["filecontent"] = pdf
	frappe.response["content_type"] = "application/pdf"


@frappe.whitelist()
def export_insurance_csv(
	property: str,
	insured_only: bool = False,
	min_value: float | None = None,
) -> None:
	"""Export insurance inventory as CSV with UTF-8 BOM.

	Args:
		property: Name of the Home Property.
		insured_only: If True, include only items marked as insured.
		min_value: Minimum estimated_value filter.
	"""
	data = get_insurance_inventory(property, insured_only, min_value)

	output = io.StringIO()
	# UTF-8 BOM for Excel compatibility
	output.write("\ufeff")

	writer = csv.writer(output)
	writer.writerow([
		_("Item Name"),
		_("Category"),
		_("Room"),
		_("Brand"),
		_("Model"),
		_("Serial Number"),
		_("Purchase Date"),
		_("Purchase Price"),
		_("Estimated Value"),
		_("Condition"),
		_("Insured"),
	])

	for item in data["items"]:
		writer.writerow([
			item.get("item_name", ""),
			item.get("category", ""),
			item.get("room_name", ""),
			item.get("brand", ""),
			item.get("model", ""),
			item.get("serial_number", ""),
			item.get("purchase_date", ""),
			item.get("purchase_price", ""),
			item.get("estimated_value", ""),
			item.get("condition", ""),
			_("Yes") if item.get("insured") else _("No"),
		])

	filename = f"Insurance_Inventory_{data['property_name']}_{today()}.csv"
	frappe.response["type"] = "download"
	frappe.response["filename"] = filename
	frappe.response["filecontent"] = output.getvalue().encode("utf-8")
	frappe.response["content_type"] = "text/csv; charset=utf-8"
