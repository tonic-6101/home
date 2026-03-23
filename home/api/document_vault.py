# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Document vault view API (Feature 34).

Read-only view layer over Frappe File records attached to property-related
DocTypes. No new DocType — queries existing attachments and groups them
into vault categories derived from the source DocType.

Child role sees the vault but financial-source documents are excluded.
Repo enrichment (tags, AI summaries) layered on when Repo is installed.
"""

from collections import defaultdict

import frappe
from frappe import _

from home.api.permission import get_household_role, require_household_access, require_role


# ---------------------------------------------------------------------------
# Category mapping
# ---------------------------------------------------------------------------

CATEGORY_MAP = {
	"Home Property": "Property",
	"Home Mortgage": "Property",
	"Home Item": "Manuals & Receipts",
	"Home Warranty": "Warranties",
	"Home Maintenance": "Receipts & Invoices",
	"Home Insurance Policy": "Insurance",
		"Home Utility Bill": "Receipts & Invoices",
	"Home Purchase Return": "Receipts & Invoices",
}

# DocTypes whose attachments are hidden from Child role (financial data)
_FINANCIAL_DOCTYPES = {
	"Home Insurance Policy",
	"Home Utility Bill",
	"Home Purchase Return",
	"Home Mortgage",
}

# Label fields used to build human-readable source labels
_LABEL_FIELDS = {
	"Home Item": "item_name",
	"Home Warranty": "warranty_type",
	"Home Maintenance": "title",
	"Home Insurance Policy": "policy_name",
		"Home Utility Bill": "bill_type",
	"Home Purchase Return": "item_description",
	"Home Mortgage": "mortgage_name",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_allowed_doctypes(role: str) -> list[str]:
	"""Return DocTypes whose attachments this role may see."""
	all_doctypes = list(CATEGORY_MAP.keys())
	if role == "Child":
		return [d for d in all_doctypes if d not in _FINANCIAL_DOCTYPES]
	return all_doctypes


def _build_record_map(property: str, doctypes: list[str]) -> dict[str, dict[str, str]]:
	"""Return {doctype: {name: label}} for all records linked to this property."""
	result: dict[str, dict[str, str]] = {}

	household = frappe.db.get_value("Home Property", property, "household")

	for dt in doctypes:
		if dt == "Home Property":
			result[dt] = {property: _("Property")}
			continue

		filter_field = "property"
		filter_value = property

		label_field = _LABEL_FIELDS.get(dt)
		fields = ["name"]
		if label_field:
			fields.append(label_field)

		rows = frappe.get_all(dt, filters={filter_field: filter_value}, fields=fields)
		result[dt] = {
			r["name"]: (r.get(label_field) or r["name"]) if label_field else r["name"]
			for r in rows
		}

	return result


def _enrich_with_repo(files: list[dict]) -> list[dict]:
	"""Add Repo metadata (tags, summaries) to file entries if available."""
	try:
		file_urls = [f["file_url"] for f in files if f.get("file_url")]
		if not file_urls:
			return files

		entries = frappe.get_all(
			"Explorer Entry",
			filters={"file_url": ["in", file_urls]},
			fields=["file_url", "title", "summary", "tags"],
		)
		entry_map = {e["file_url"]: e for e in entries}
		for f in files:
			entry = entry_map.get(f.get("file_url"))
			if entry:
				f["repo_title"] = entry.get("title")
				f["repo_summary"] = entry.get("summary")
				f["repo_tags"] = entry.get("tags") or []
	except Exception:
		pass  # Repo unavailable or schema mismatch — degrade silently
	return files


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_vault(property: str, category: str = "all") -> dict:
	"""Get all documents attached to a property and its related records.

	Files are grouped into vault categories: Manuals & Receipts, Warranties,
	Insurance, Receipts & Invoices, Property, Other. Child role sees the
	vault but financial-source documents are excluded.

	Args:
		property: Name of the Home Property record.
		category: Filter to a single vault category, or "all" (default).

	Returns:
		dict with groups (by category), total count, category_filter,
		and repo_active flag.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)

	role = get_household_role(prop.household)
	allowed_doctypes = _get_allowed_doctypes(role)
	record_map = _build_record_map(property, allowed_doctypes)

	# Query Frappe File table for attachments on those records
	files: list[dict] = []
	seen: set[str] = set()

	for doctype, records in record_map.items():
		if not records:
			continue

		file_rows = frappe.get_all(
			"File",
			filters={
				"attached_to_doctype": doctype,
				"attached_to_name": ["in", list(records.keys())],
			},
			fields=[
				"name", "file_name", "file_url", "file_size",
				"is_private", "creation", "attached_to_name",
			],
			order_by="creation desc",
		)

		vault_category = CATEGORY_MAP.get(doctype, "Other")
		for f in file_rows:
			if f["name"] in seen:
				continue
			seen.add(f["name"])
			files.append({
				"file_name": f["file_name"],
				"file_url": f["file_url"],
				"file_size": f["file_size"],
				"is_private": f["is_private"],
				"added": str(f["creation"] or ""),
				"source_doctype": doctype,
				"source_name": f["attached_to_name"],
				"source_label": records.get(f["attached_to_name"], f["attached_to_name"]),
				"vault_category": vault_category,
			})

	# Repo enrichment (soft integration)
	repo_active = "repo" in frappe.get_installed_apps()
	if repo_active:
		files = _enrich_with_repo(files)

	# Filter by category
	if category != "all":
		files = [f for f in files if f["vault_category"] == category]

	# Group by category, sorted newest first
	grouped: dict[str, list[dict]] = defaultdict(list)
	for f in sorted(files, key=lambda x: x["added"], reverse=True):
		grouped[f["vault_category"]].append(f)

	return {
		"property": property,
		"category_filter": category,
		"groups": dict(grouped),
		"total": len(files),
		"repo_active": repo_active,
	}


@frappe.whitelist()
def get_link_targets(property: str) -> dict:
	"""Return available DocTypes and their records for the upload dialog.

	Used by the frontend to populate the "Link to" dropdowns when
	uploading a document from the vault.

	Args:
		property: Name of the Home Property record.

	Returns:
		dict with a targets list, each containing doctype, label, and records.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)

	role = get_household_role(prop.household)
	allowed_doctypes = _get_allowed_doctypes(role or "Child")
	record_map = _build_record_map(property, allowed_doctypes)

	targets = []
	for doctype, records in record_map.items():
		targets.append({
			"doctype": doctype,
			"label": doctype.replace("Home ", ""),
			"records": [
				{"name": name, "label": label}
				for name, label in records.items()
			],
		})

	return {"targets": targets}


@frappe.whitelist()
def upload_to_record(property: str, doctype: str, record: str, file_url: str) -> dict:
	"""Attach an already-uploaded file to a specific source record.

	The frontend uploads the file first via Frappe's standard upload API,
	then calls this to re-attach it to the correct source record so it
	appears in the vault under the right category.

	Args:
		property: Name of the Home Property record (for access check).
		doctype: Target DocType (e.g. "Home Item").
		record: Target record name.
		file_url: URL of the already-uploaded file.

	Returns:
		dict with file_name, file_url, and attached_to info.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	# Validate the target record belongs to this property
	allowed_doctypes = _get_allowed_doctypes("Adult")
	if doctype not in allowed_doctypes:
		frappe.throw(_("Invalid target DocType"))

	record_map = _build_record_map(property, [doctype])
	if record not in record_map.get(doctype, {}):
		frappe.throw(_("Record does not belong to this property"))

	# Find the uploaded file and re-attach it to the target record
	file_doc = frappe.get_all(
		"File",
		filters={"file_url": file_url},
		fields=["name"],
		order_by="creation desc",
		limit=1,
	)

	if not file_doc:
		frappe.throw(_("File not found"))

	frappe.db.set_value(
		"File", file_doc[0]["name"],
		{
			"attached_to_doctype": doctype,
			"attached_to_name": record,
		},
	)

	return {
		"file_name": file_url.rsplit("/", 1)[-1],
		"file_url": file_url,
		"attached_to_doctype": doctype,
		"attached_to_name": record,
	}
