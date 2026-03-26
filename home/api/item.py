# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Item tracking APIs (Features 5, 6, 14, 19b).

Core CRUD-adjacent endpoints for listing and retrieving items (appliances
and possessions), the disposal-to-return flow, barcode/OCR scan-to-register,
and insurance inventory export.
"""

import base64
import csv
import io
import re

import frappe
from frappe import _
from frappe.utils import today

from home.api.permission import (
	get_household_role,
	require_household_access,
	require_role,
)

# Financial fields stripped from Child role responses
_FINANCIAL_FIELDS = ("purchase_price", "estimated_value")


# ---------------------------------------------------------------------------
# Item listing (merged from appliance + inventory)
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_items(
	property: str,
	item_type: str | None = None,
	category: str | None = None,
	room: str | None = None,
) -> dict:
	"""Return items for a property, with optional type/category/room filters.

	Args:
		property: Name of the Home Property record.
		item_type: Optional filter — 'Appliance', 'Possession', or 'Fixture'.
		category: Optional category filter.
		room: Optional room filter.

	Returns:
		dict with "items" list ordered by room then name,
		and "warranties" list for the Warranties tab.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)

	filters: dict = {"property": property}
	if item_type:
		filters["item_type"] = item_type
	if category:
		filters["category"] = category
	if room:
		filters["room"] = room

	# Exclude disposed appliances by default
	if item_type == "Appliance":
		filters["status"] = ["!=", "Disposed"]

	items = frappe.get_all(
		"Home Item",
		filters=filters,
		fields=[
			"name",
			"item_name",
			"item_type",
			"category",
			"brand",
			"model",
			"status",
			"condition",
			"purchase_date",
			"purchase_price",
			"estimated_value",
			"room",
			"photo",
			"insured",
			"expected_lifespan_years",
			"installed_date",
			"material",
		],
		order_by="room asc, item_name asc",
	)

	# Strip financial fields for Child role
	role = get_household_role(doc.household)
	if role == "Child":
		for item in items:
			for field in _FINANCIAL_FIELDS:
				item.pop(field, None)

	# Compute summary stats (non-Child only)
	total_value = 0
	insured_value = 0
	insured_count = 0
	if role != "Child":
		for item in items:
			ev = item.get("estimated_value") or 0
			total_value += ev
			if item.get("insured"):
				insured_value += ev
				insured_count += 1

	# Warranty rows for the Warranties tab
	from frappe.utils import date_diff

	warranty_rows: list[dict] = []
	if role != "Child":
		warranties = frappe.get_all(
			"Home Warranty",
			filters={"property": property},
			fields=[
				"name as warranty_name",
				"item",
				"warranty_type",
				"provider",
				"end_date",
				"burden_of_proof_date",
			],
			order_by="end_date asc",
		)
		for w in warranties:
			days_remaining = date_diff(w["end_date"], today())
			if days_remaining < 0:
				expiry_status = "expired"
			elif days_remaining <= 30:
				expiry_status = "expiring_soon"
			else:
				expiry_status = "active"
			w["days_remaining"] = max(days_remaining, 0)
			w["expiry_status"] = expiry_status
			# Resolve item_name
			w["item_name"] = frappe.db.get_value("Home Item", w["item"], "item_name") or w["item"]
			warranty_rows.append(w)

	result: dict = {"items": items, "warranties": warranty_rows}
	if role != "Child":
		result["total_estimated_value"] = total_value
		result["insured_value"] = insured_value
		result["insured_count"] = insured_count

	return result


@frappe.whitelist()
def get_item(name: str) -> dict:
	"""Return full item detail with linked record counts and lifetime cost.

	Args:
		name: Name of the Home Item record.

	Returns:
		dict with all item fields plus maintenance_count,
		warranty_count, and lifetime_cost (for appliances).
	"""
	doc = frappe.get_doc("Home Item", name)
	require_household_access(doc.household)

	result = doc.as_dict()

	if doc.item_type in ("Appliance", "Fixture"):
		# Task cost from Orga Tasks linked to this item (post task-unification)
		task_cost = 0
		task_count = 0
		if "orga" in frappe.get_installed_apps() and frappe.get_meta("Orga Task").has_field("home_item"):
			task_cost = frappe.db.sql(
				"""SELECT COALESCE(SUM(actual_cost), 0)
				   FROM `tabOrga Task`
				   WHERE home_item = %s AND status = 'Completed'""",
				name,
			)[0][0] or 0
			task_count = frappe.db.count("Orga Task", {"home_item": name})

		result["maintenance_count"] = task_count
		result["warranty_count"] = frappe.db.count("Home Warranty", {"item": name})
		result["lifetime_cost"] = (doc.purchase_price or 0) + task_cost

		# Task history list
		if task_count:
			result["maintenance_history"] = frappe.get_all(
				"Orga Task",
				filters={"home_item": name},
				fields=["name", "subject as title", "status", "start_date as scheduled_date", "completed_date"],
				order_by="start_date desc",
			)
		else:
			result["maintenance_history"] = []

		# Warranty list for the Warranties tab
		from frappe.utils import date_diff

		warranty_rows = frappe.get_all(
			"Home Warranty",
			filters={"item": name},
			fields=[
				"name", "warranty_type", "provider", "start_date",
				"end_date", "burden_of_proof_date", "document",
			],
			order_by="end_date asc",
		)
		for w in warranty_rows:
			days_remaining = date_diff(w["end_date"], today()) if w.get("end_date") else 0
			if days_remaining < 0:
				w["expiry_status"] = "expired"
			elif days_remaining <= 30:
				w["expiry_status"] = "expiring_soon"
			else:
				w["expiry_status"] = "active"
			w["days_remaining"] = max(days_remaining, 0)
			w["claim_count"] = frappe.db.count(
				"Home Warranty Claim", {"parent": w["name"]}
			)
		result["warranties"] = warranty_rows

	# Strip financial fields for Child role
	role = get_household_role(doc.household)
	if role == "Child":
		for key in _FINANCIAL_FIELDS + ("lifetime_cost",):
			result.pop(key, None)

	return result


@frappe.whitelist()
def create_return_from_disposal(item: str) -> dict:
	"""Create a Home Purchase Return pre-filled from a disposed item.

	Called by the frontend after the disposal prompt is confirmed.

	Args:
		item: Name of the Home Item record (must have status=Disposed).

	Returns:
		dict with "purchase_return" name of the created record.
	"""
	doc = frappe.get_doc("Home Item", item)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	if doc.status != "Disposed":
		frappe.throw(_("Item must be in Disposed status to create a return record"))

	purchase_return = frappe.get_doc(
		{
			"doctype": "Home Purchase Return",
			"property": doc.property,
			"item_description": doc.item_name,
			"linked_item": doc.name,
			"purchase_date": doc.purchase_date,
			"purchase_price": doc.purchase_price,
			"return_date": today(),
			"return_reason": "Defective",
			"refund_status": "Pending",
		}
	).insert()

	return {"purchase_return": purchase_return.name}


# ---------------------------------------------------------------------------
# Insurance summary (from inventory.py)
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_insurance_summary(property: str) -> dict:
	"""Return insurance summary for a property. Owner/Adult only.

	Includes total value, insured/uninsured split, and breakdown by category.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	items = frappe.get_all(
		"Home Item",
		filters={"property": property},
		fields=["item_name", "item_type", "category", "estimated_value", "insured"],
	)

	total_value = 0
	insured_value = 0
	insured_count = 0
	by_category: dict[str, dict] = {}
	by_type: dict[str, dict] = {}

	for item in items:
		ev = item.get("estimated_value") or 0
		total_value += ev

		if item.get("insured"):
			insured_value += ev
			insured_count += 1

		cat = item.get("category") or "Other"
		if cat not in by_category:
			by_category[cat] = {"category": cat, "value": 0, "count": 0, "has_insured": False}
		by_category[cat]["value"] += ev
		by_category[cat]["count"] += 1
		if item.get("insured"):
			by_category[cat]["has_insured"] = True

		item_type = item.get("item_type") or "Other"
		if item_type not in by_type:
			by_type[item_type] = {"item_type": item_type, "value": 0, "count": 0}
		by_type[item_type]["value"] += ev
		by_type[item_type]["count"] += 1

	categories = sorted(by_category.values(), key=lambda c: c["value"], reverse=True)
	types = sorted(by_type.values(), key=lambda t: t["value"], reverse=True)

	return {
		"property": property,
		"property_name": doc.property_name,
		"total_estimated_value": total_value,
		"insured_value": insured_value,
		"insured_count": insured_count,
		"uninsured_value": total_value - insured_value,
		"item_count": len(items),
		"categories": categories,
		"types": types,
	}


# ---------------------------------------------------------------------------
# Feature 7 — Item Health Forecast (appliances only)
# ---------------------------------------------------------------------------


def _compute_recommendation(
	pct_used: int | None, ratio: int | None, status: str
) -> dict:
	"""Return {level, message} where level is good | monitor | replace | unknown.

	Language is always advisory — never commanding.
	"""
	if status in ("Disposed", "Broken"):
		return {
			"level": "replace",
			"message": _("This item is no longer in service."),
		}

	signals: list[str] = []

	if pct_used is not None:
		if pct_used >= 100:
			signals.append("past_lifespan")
		elif pct_used >= 80:
			signals.append("near_end")

	if ratio is not None:
		if ratio >= 75:
			signals.append("high_repair_cost")
		elif ratio >= 50:
			signals.append("notable_repair_cost")

	if "past_lifespan" in signals or "high_repair_cost" in signals:
		return {
			"level": "replace",
			"message": _(
				"Consider budgeting for a replacement — this item is past "
				"its expected lifespan or has high accumulated repair costs."
			),
		}

	if "near_end" in signals or "notable_repair_cost" in signals:
		return {
			"level": "monitor",
			"message": _(
				"Keep an eye on this item — it is approaching the end of "
				"its expected lifespan or has notable repair costs."
			),
		}

	if pct_used is None and ratio is None:
		return {
			"level": "unknown",
			"message": _(
				"Add a purchase date and expected lifespan to see a health forecast."
			),
		}

	return {
		"level": "good",
		"message": _("This item is in good shape — no action needed."),
	}


def compute_health(item_name: str) -> dict:
	"""Compute health forecast metrics for a single item.

	All values are computed at read time — nothing is stored.
	"""
	from frappe.utils import date_diff, getdate

	doc = frappe.get_doc("Home Item", item_name)
	result: dict = {"item": item_name}

	# --- Age ---
	age_years: float | None = None
	if doc.purchase_date:
		age_days = date_diff(today(), doc.purchase_date)
		age_years = age_days / 365.25
		result["age_years"] = round(age_years, 1)
	else:
		result["age_years"] = None

	# --- Lifespan progress ---
	lifespan = doc.expected_lifespan_years
	if age_years is not None and lifespan:
		pct_used = min(age_years / lifespan, 1.0)
		result["lifespan_pct_used"] = round(pct_used * 100)
		result["years_remaining"] = max(round(lifespan - age_years, 1), 0)
		result["estimated_replacement_year"] = int(
			getdate(doc.purchase_date).year + lifespan
		)
	else:
		result["lifespan_pct_used"] = None
		result["years_remaining"] = None
		result["estimated_replacement_year"] = None

	# --- Repair costs (from Orga Tasks post task-unification) ---
	repair_total = 0
	repair_count = 0
	if "orga" in frappe.get_installed_apps() and frappe.get_meta("Orga Task").has_field("home_item"):
		repair_total = frappe.db.sql(
			"""SELECT COALESCE(SUM(actual_cost), 0)
			   FROM `tabOrga Task`
			   WHERE home_item = %s AND status = 'Completed' AND actual_cost > 0""",
			item_name,
		)[0][0] or 0
		repair_count = frappe.db.count(
			"Orga Task",
			{"home_item": item_name, "status": "Completed"},
		)
	result["repair_total"] = repair_total
	result["repair_count"] = repair_count

	# --- Cost ratio (50% rule proxy) ---
	if doc.purchase_price and doc.purchase_price > 0:
		result["repair_to_purchase_ratio"] = round(
			repair_total / doc.purchase_price * 100
		)
	else:
		result["repair_to_purchase_ratio"] = None

	# --- Recommendation ---
	result["recommendation"] = _compute_recommendation(
		pct_used=result.get("lifespan_pct_used"),
		ratio=result.get("repair_to_purchase_ratio"),
		status=doc.status,
	)

	return result


@frappe.whitelist()
def get_health(name: str) -> dict:
	"""Return item health forecast with role-gated financial data.

	Child role sees age bar and recommendation but not repair costs or ratio.
	"""
	doc = frappe.get_doc("Home Item", name)
	require_household_access(doc.household)

	result = compute_health(name)

	role = get_household_role(doc.household)
	if role == "Child":
		result.pop("repair_total", None)
		result.pop("repair_to_purchase_ratio", None)
		result.pop("repair_count", None)

	return result


# ---------------------------------------------------------------------------
# Feature 6 — Scan to register helpers
# ---------------------------------------------------------------------------


def _require_household_access_by_property(property_name: str) -> None:
	"""Verify household access via a property name."""
	household = frappe.db.get_value("Home Property", property_name, "household")
	if not household:
		frappe.throw(_("Property not found"), frappe.DoesNotExistError)
	require_household_access(household)


def _infer_category(brand: str, model: str) -> str:
	"""Best-effort category inference from brand/model keywords.

	Returns one of the Home Item category options or empty string.
	"""
	text = f"{brand} {model}".lower()

	rules: list[tuple[str, tuple[str, ...]]] = [
		("HVAC", ("air condition", "hvac", "ventilat", "fan", "dehumidif", "humidif")),
		("Heating", ("boiler", "furnace", "radiator", "heater", "thermostat", "heat pump")),
		("White Goods", (
			"washer", "washing", "dryer", "dishwasher", "refrigerat", "fridge",
			"freezer", "oven", "cooker", "tumble",
		)),
		("Kitchen", (
			"microwave", "blender", "mixer", "toaster", "kettle", "coffee",
			"espresso", "food processor", "induction", "hob", "extractor",
		)),
		("Electronics", ("tv", "television", "monitor", "speaker", "soundbar", "laptop", "computer")),
		("Plumbing", ("pump", "valve", "tap", "faucet", "shower", "toilet")),
	]

	for category, keywords in rules:
		for kw in keywords:
			if kw in text:
				return category

	return ""


def _confidence(value: str | None) -> str:
	"""Return ``'high'`` if value looks non-empty and well-formed, else ``'low'``."""
	if not value or len(value.strip()) < 2:
		return "low"
	return "high"


# ---------------------------------------------------------------------------
# Feature 6 — OCR extraction backends
# ---------------------------------------------------------------------------


def _extract_via_jana(image_b64: str) -> dict:
	"""Extract item fields via Jana vision API."""
	try:
		from jana.api.vision import extract_structured  # type: ignore[import-untyped]

		result = extract_structured(
			image_b64=image_b64,
			prompt=(
				"Extract the following fields from this appliance rating plate image: "
				"brand (manufacturer name), model (model number/name), "
				"serial_number (serial number). Return as JSON with keys: "
				"brand, model, serial_number. If a field is not visible, return empty string."
			),
		)

		brand = (result.get("brand") or "").strip()
		model = (result.get("model") or "").strip()
		serial_number = (result.get("serial_number") or "").strip()

		return {
			"brand": brand,
			"model": model,
			"serial_number": serial_number,
			"category": _infer_category(brand, model),
			"confidence": {
				"brand": _confidence(brand),
				"model": _confidence(model),
				"serial_number": _confidence(serial_number),
				"category": "low",
			},
			"method": "jana",
		}
	except Exception:
		frappe.log_error(
			title=_("Jana vision extraction failed"),
			message=frappe.get_traceback(),
		)
		return _extract_via_tesseract(image_b64)


def _extract_via_tesseract(image_b64: str) -> dict:
	"""Extract item fields via Tesseract OCR (fallback)."""
	brand = ""
	model = ""
	serial_number = ""

	try:
		import pytesseract  # type: ignore[import-untyped]
		from PIL import Image  # type: ignore[import-untyped]

		image_data = base64.b64decode(image_b64)
		image = Image.open(io.BytesIO(image_data))

		text = pytesseract.image_to_string(image)
		lines = [line.strip() for line in text.split("\n") if line.strip()]

		for line in lines:
			line_lower = line.lower()

			# Brand detection
			if not brand:
				for prefix in ("brand:", "manufacturer:", "hersteller:", "marke:"):
					if prefix in line_lower:
						brand = line.split(":", 1)[1].strip()
						break
				if not brand and re.match(r"^[A-Z][A-Za-z\s]{2,20}$", line):
					brand = line.strip()

			# Model detection
			if not model:
				for prefix in ("model:", "modell:", "type:", "typ:"):
					if prefix in line_lower:
						model = line.split(":", 1)[1].strip()
						break
				if not model:
					match = re.search(r"[A-Z]{2,4}[\d]{2,}[A-Z\d]*", line)
					if match:
						model = match.group()

			# Serial number detection
			if not serial_number:
				for prefix in ("serial:", "s/n:", "ser.nr.:", "seriennr.:"):
					if prefix in line_lower:
						serial_number = line.split(":", 1)[1].strip()
						break
				if not serial_number:
					match = re.search(
						r"(?:S/?N|Serial)[:\s]*([A-Z0-9\-]{6,})", line, re.IGNORECASE
					)
					if match:
						serial_number = match.group(1)
	except ImportError:
		frappe.log_error(
			title=_("Tesseract/Pillow not available"),
			message="pytesseract or Pillow not installed — OCR extraction unavailable",
		)
	except Exception:
		frappe.log_error(
			title=_("Tesseract OCR extraction failed"),
			message=frappe.get_traceback(),
		)

	return {
		"brand": brand,
		"model": model,
		"serial_number": serial_number,
		"category": _infer_category(brand, model),
		"confidence": {
			"brand": _confidence(brand),
			"model": _confidence(model),
			"serial_number": _confidence(serial_number),
			"category": "low",
		},
		"method": "tesseract",
	}


# ---------------------------------------------------------------------------
# Feature 6 — Public API endpoints
# ---------------------------------------------------------------------------


@frappe.whitelist()
def extract_from_image(image_b64: str, property: str) -> dict:
	"""Extract brand, model, serial number from a rating plate photo.

	Uses Jana vision API if installed, falls back to Tesseract OCR.

	Args:
		image_b64: Base64-encoded image data (JPEG or PNG).
		property: Name of the Home Property (for access control).

	Returns:
		dict with brand, model, serial_number, category, confidence, method.
	"""
	_require_household_access_by_property(property)

	if "jana" in frappe.get_installed_apps():
		return _extract_via_jana(image_b64)

	return _extract_via_tesseract(image_b64)


@frappe.whitelist()
def lookup_barcode(barcode: str, property: str) -> dict:
	"""Look up product info from an EAN/UPC barcode via UPCitemdb.

	The barcode is decoded client-side; this endpoint does the product
	database lookup.

	Args:
		barcode: EAN-13 or UPC-A barcode string.
		property: Name of the Home Property (for access control).

	Returns:
		dict with found (bool), and if found: brand, model, category.
	"""
	_require_household_access_by_property(property)

	import requests

	try:
		response = requests.get(
			"https://api.upcitemdb.com/prod/trial/lookup",
			params={"upc": barcode},
			timeout=5,
		)
		if response.ok:
			data = response.json()
			items = data.get("items", [])
			if items:
				first = items[0]
				brand = (first.get("brand") or "").strip()
				model_name = (first.get("model") or first.get("title") or "").strip()
				return {
					"found": True,
					"brand": brand,
					"model": model_name,
					"category": _infer_category(brand, model_name),
				}
	except Exception:
		frappe.log_error(
			title=_("UPCitemdb lookup failed"),
			message=frappe.get_traceback(),
		)

	return {"found": False}


@frappe.whitelist()
def check_recall(brand: str, model: str) -> dict:
	"""Check EU RAPEX / Safety Gate for recalls matching brand + model.

	Called once at item registration time after the user confirms
	the extracted fields. Failures are silent — no error shown to user.

	Args:
		brand: Item brand name.
		model: Item model name/number.

	Returns:
		dict with recall_found (bool), and if found: title, url.
	"""
	if not brand and not model:
		return {"recall_found": False}

	import requests

	try:
		response = requests.get(
			"https://ec.europa.eu/safety-gate-alerts/api/rapex/v2/products",
			params={"q": f"{brand} {model}", "language": "en"},
			timeout=5,
		)
		if response.ok:
			results = response.json().get("results", [])
			if results:
				first = results[0]
				return {
					"recall_found": True,
					"title": first.get("productName") or first.get("title", ""),
					"url": first.get("url", ""),
				}
	except Exception:
		# Silent failure — recall check is best-effort
		pass

	return {"recall_found": False}


# ---------------------------------------------------------------------------
# Feature 19b — Insurance Inventory Export (from inventory.py)
# ---------------------------------------------------------------------------

_ITEM_FIELDS = [
	"item_name",
	"item_type",
	"category",
	"room",
	"brand",
	"model",
	"serial_number",
	"condition",
	"status",
	"material",
	"purchase_date",
	"purchase_price",
	"estimated_value",
	"insured",
	"photo",
	"notes",
]

_CSV_COLUMNS = [
	"item_name",
	"item_type",
	"category",
	"room",
	"brand",
	"model",
	"serial_number",
	"condition",
	"status",
	"material",
	"purchase_date",
	"purchase_price",
	"estimated_value",
	"insured",
	"notes",
]


def _get_filtered_items(
	property: str, include: str, min_value: float
) -> list[dict]:
	"""Fetch items with optional insured/value filters.

	Includes all item types (Appliance, Possession, Fixture) that have
	an estimated_value set. Items without estimated_value are excluded
	from insurance exports.
	"""
	filters: dict = {"property": property, "estimated_value": [">", 0]}
	if include == "insured_only":
		filters["insured"] = 1

	items = frappe.get_all(
		"Home Item",
		filters=filters,
		fields=_ITEM_FIELDS,
		order_by="item_type asc, category asc, item_name asc",
	)

	if min_value > 0:
		items = [i for i in items if (i.get("estimated_value") or 0) >= min_value]

	# Resolve room name from Link field
	for item in items:
		if item.get("room"):
			item["room_name"] = frappe.db.get_value("Home Room", item["room"], "room_name") or item["room"]
		else:
			item["room_name"] = ""

	return items


def _group_by_category(items: list[dict]) -> list[dict]:
	"""Group items by category, computing totals per group."""
	by_cat: dict[str, dict] = {}
	for item in items:
		cat = item.get("category") or "Other"
		if cat not in by_cat:
			by_cat[cat] = {
				"category": cat,
				"value": 0,
				"count": 0,
				"has_insured": False,
				"items": [],
			}
		by_cat[cat]["items"].append(item)
		by_cat[cat]["value"] += item.get("estimated_value") or 0
		by_cat[cat]["count"] += 1
		if item.get("insured"):
			by_cat[cat]["has_insured"] = True

	return sorted(by_cat.values(), key=lambda c: c["value"], reverse=True)


@frappe.whitelist()
def export_pdf(
	property: str, include: str = "all", min_value: float = 0
) -> None:
	"""Generate and stream a PDF insurance inventory report."""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	items = _get_filtered_items(property, include, float(min_value))
	categories = _group_by_category(items)

	total_value = sum(i.get("estimated_value") or 0 for i in items)
	insured_value = sum(
		(i.get("estimated_value") or 0) for i in items if i.get("insured")
	)
	insured_count = sum(1 for i in items if i.get("insured"))

	currency = frappe.defaults.get_global_default("currency") or "EUR"

	html = frappe.render_template(
		"home/templates/includes/insurance_inventory.html",
		{
			"property": prop,
			"categories": categories,
			"total_value": total_value,
			"insured_value": insured_value,
			"insured_count": insured_count,
			"item_count": len(items),
			"currency": currency,
			"generated_date": frappe.utils.formatdate(today()),
			"prepared_by": frappe.utils.get_fullname(frappe.session.user),
		},
	)

	pdf_bytes = frappe.utils.pdf.get_pdf(html)

	filename = f"inventory-{today()}.pdf"
	frappe.local.response.filename = filename
	frappe.local.response.filecontent = pdf_bytes
	frappe.local.response.type = "download"


@frappe.whitelist()
def export_csv(
	property: str, include: str = "all", min_value: float = 0
) -> None:
	"""Generate and stream a CSV inventory export."""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	items = _get_filtered_items(property, include, float(min_value))

	output = io.StringIO()
	writer = csv.DictWriter(output, fieldnames=_CSV_COLUMNS, extrasaction="ignore")
	writer.writeheader()
	for item in items:
		writer.writerow({k: item.get(k, "") for k in _CSV_COLUMNS})

	filename = f"inventory-{today()}.csv"
	frappe.local.response.filename = filename
	frappe.local.response.filecontent = "\ufeff" + output.getvalue()  # UTF-8 BOM
	frappe.local.response.type = "download"
