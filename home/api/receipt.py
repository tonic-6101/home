# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Receipt scanning API (Feature 15).

Extract purchase date, price, and retailer from a receipt photo using
Jana vision API (if installed) or Tesseract OCR fallback. Always returns
a result — failures produce null fields with low confidence so the user
can fill in details manually.
"""

import base64
import os
import re
import tempfile

import frappe
from frappe import _
from frappe.utils import getdate

from home.api.permission import require_household_access, require_role

_SUPPORTED_DOCTYPES = ("Home Item",)


@frappe.whitelist()
def extract_receipt(image_b64: str, doctype: str, name: str) -> dict:
	"""Extract purchase date, amount, and retailer from a receipt image.

	Uses Jana vision API if installed, Tesseract otherwise.
	All failures return null fields with low confidence — never raises
	a user-facing error.

	Args:
		image_b64: Base64-encoded receipt image (JPEG/PNG).
		doctype: 'Home Item'.
		name: Document name.

	Returns:
		dict with purchase_date, purchase_price, retailer, and
		per-field confidence levels (high/low).
	"""
	if doctype not in _SUPPORTED_DOCTYPES:
		frappe.throw(_("Unsupported document type"))

	doc = frappe.get_doc(doctype, name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	if "jana" in frappe.get_installed_apps():
		return _extract_via_jana(image_b64)

	return _extract_via_tesseract(image_b64)


@frappe.whitelist()
def save_receipt(
	doctype: str,
	name: str,
	purchase_date: str | None = None,
	purchase_price: float | None = None,
	image_b64: str | None = None,
) -> dict:
	"""Save confirmed receipt data to the target record.

	Writes purchase_date and purchase_price to the document, and saves
	the receipt image as a Frappe File attachment linked to the appropriate
	field (receipt_photo for Appliance type, receipt for Possession type).

	Args:
		doctype: 'Home Item'.
		name: Document name.
		purchase_date: ISO date string (optional).
		purchase_price: Amount as float (optional).
		image_b64: Base64-encoded receipt image to save (optional).

	Returns:
		dict with ok flag.
	"""
	if doctype not in _SUPPORTED_DOCTYPES:
		frappe.throw(_("Unsupported document type"))

	doc = frappe.get_doc(doctype, name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	if purchase_date:
		doc.purchase_date = purchase_date
	if purchase_price is not None:
		doc.purchase_price = purchase_price

	if image_b64:
		receipt_field = (
			"receipt_photo" if doc.item_type == "Appliance" else "receipt"
		)
		file_doc = _save_image_attachment(image_b64, doctype, name)
		setattr(doc, receipt_field, file_doc.file_url)

	doc.save()
	return {"ok": True}


# ---------------------------------------------------------------------------
# Internal extraction helpers
# ---------------------------------------------------------------------------

_EMPTY_RESULT = {
	"purchase_date": None,
	"purchase_price": None,
	"retailer": None,
	"confidence": {
		"purchase_date": "low",
		"purchase_price": "low",
		"retailer": "low",
	},
}


def _extract_via_jana(image_b64: str) -> dict:
	"""Use Jana vision API with receipt-specific extraction prompt.

	Stubbed — returns empty result until Jana integration is wired up.
	In production, calls jana.api.vision.extract with a receipt prompt
	and parses the structured JSON response.
	"""
	# TODO: implement Jana vision API call
	# Prompt: "Extract the total amount, purchase date, and retailer name
	# from this receipt. Return JSON with keys: purchase_date (ISO 8601),
	# purchase_price (float, total after tax), retailer (string)."
	return _EMPTY_RESULT.copy()


def _extract_via_tesseract(image_b64: str) -> dict:
	"""Tesseract OCR with regex post-processing for date and currency patterns."""
	import subprocess

	try:
		image_data = base64.b64decode(image_b64)
	except Exception:
		return _EMPTY_RESULT.copy()

	tmp_path = None
	try:
		with tempfile.NamedTemporaryFile(
			suffix=".jpg", delete=False
		) as f:
			f.write(image_data)
			tmp_path = f.name

		text = subprocess.check_output(
			["tesseract", tmp_path, "stdout", "--psm", "6"],
			stderr=subprocess.DEVNULL,
			timeout=30,
		).decode("utf-8", errors="ignore")
	except Exception:
		return _EMPTY_RESULT.copy()
	finally:
		if tmp_path and os.path.exists(tmp_path):
			os.unlink(tmp_path)

	# Date patterns: DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD
	date_match = re.search(
		r"(\d{2}[./]\d{2}[./]\d{4}|\d{4}-\d{2}-\d{2})", text
	)
	parsed_date = _parse_date(date_match.group(1)) if date_match else None

	# Currency amounts: find all decimal amounts, take the largest as total
	amounts = re.findall(r"\d+[,.]\d{2}", text)
	parsed_amounts = []
	for a in amounts:
		try:
			parsed_amounts.append(float(a.replace(",", ".")))
		except ValueError:
			continue
	price = max(parsed_amounts) if parsed_amounts else None

	return {
		"purchase_date": parsed_date,
		"purchase_price": price,
		"retailer": None,  # Tesseract cannot reliably identify retailer name
		"confidence": {
			"purchase_date": "high" if parsed_date else "low",
			"purchase_price": "low",  # max-amount heuristic is always low
			"retailer": "low",
		},
	}


def _parse_date(date_str: str) -> str | None:
	"""Parse a date string in DD.MM.YYYY, DD/MM/YYYY, or YYYY-MM-DD format.

	Returns ISO date string (YYYY-MM-DD) or None on failure.
	"""
	if not date_str:
		return None

	try:
		# Already ISO format
		if "-" in date_str and len(date_str) == 10:
			getdate(date_str)
			return date_str

		# European format: DD.MM.YYYY or DD/MM/YYYY
		sep = "." if "." in date_str else "/"
		parts = date_str.split(sep)
		if len(parts) == 3:
			iso = f"{parts[2]}-{parts[1]}-{parts[0]}"
			getdate(iso)  # validate
			return iso
	except Exception:
		pass

	return None


def _save_image_attachment(
	image_b64: str, doctype: str, name: str
) -> "frappe.core.doctype.file.file.File":
	"""Save a base64-encoded image as a Frappe File attachment."""
	image_data = base64.b64decode(image_b64)

	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"receipt_{name}.jpg",
			"attached_to_doctype": doctype,
			"attached_to_name": name,
			"content": image_data,
			"is_private": 1,
		}
	)
	file_doc.save(ignore_permissions=True)
	return file_doc
