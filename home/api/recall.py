# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Appliance recall monitoring API (Feature 57).

Provides endpoints for dismissing recall alerts, on-demand recall checks,
and internal matching logic for the EU Safety Gate scheduled task.
The actual EU Safety Gate fetch is stubbed for now — the matching and
de-duplication logic is fully implemented.
"""

import frappe
from frappe import _
from frappe.utils import today

from home.api.permission import require_household_access, require_role


@frappe.whitelist()
def dismiss_recall(item: str, recall_idx: int) -> dict:
	"""Dismiss a specific recall alert on an item.

	Sets dismissed=1, dismissed_date=today, dismissed_by=current user
	on the child row identified by idx.

	Args:
		item: Name of the Home Item record.
		recall_idx: The idx of the recall child row to dismiss.

	Returns:
		dict with recall_id and dismissed status.
	"""
	doc = frappe.get_doc("Home Item", item)
	prop = frappe.get_doc("Home Property", doc.property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	recall_idx = int(recall_idx)
	recall_row = None
	for row in doc.recalls:
		if row.idx == recall_idx:
			recall_row = row
			break

	if not recall_row:
		frappe.throw(
			_("Recall row with idx {0} not found on appliance {1}").format(
				recall_idx, item
			)
		)

	if recall_row.dismissed:
		return {
			"recall_id": recall_row.recall_id,
			"already_dismissed": True,
		}

	recall_row.dismissed = 1
	recall_row.dismissed_date = today()
	recall_row.dismissed_by = frappe.session.user
	doc.save(ignore_permissions=False)

	return {
		"recall_id": recall_row.recall_id,
		"already_dismissed": False,
	}


@frappe.whitelist()
def check_single_item(item: str) -> list[dict]:
	"""On-demand recall check for a single item.

	Fetches alerts from the EU Safety Gate (currently stubbed) and runs
	the matching logic against the appliance. Updates last_recall_check.

	Args:
		item: Name of the Home Item record.

	Returns:
		list of newly matched recall dicts (empty if no new matches).
	"""
	doc = frappe.get_doc("Home Item", item)
	prop = frappe.get_doc("Home Property", doc.property)
	require_household_access(prop.household)

	# Fetch alerts from EU Safety Gate — stubbed for now
	alerts = _fetch_eu_safety_gate_alerts(doc.category, doc.brand)

	new_recalls = _match_recalls(doc, alerts)

	# Update last_recall_check regardless of whether new recalls were found
	doc.last_recall_check = today()
	doc.save(ignore_permissions=False)

	return new_recalls


def _match_recalls(item_doc, alerts: list[dict]) -> list[dict]:
	"""Match recall alerts against an item and create child rows.

	Takes an item doc and a list of alert dicts. Matches by category
	and brand (case-insensitive). De-duplicates against existing child rows
	by recall_id. Creates new child rows for matches.

	Args:
		item_doc: The Home Item document.
		alerts: list of dicts, each with keys: recall_id, title, category,
			brand, severity, published_date, detail_url.

	Returns:
		list of newly added recall dicts.
	"""
	if not alerts:
		return []

	item_category = (item_doc.category or "").lower()
	item_brand = (item_doc.brand or "").lower()

	# Collect existing recall_ids for de-duplication
	existing_ids = {
		row.recall_id for row in (item_doc.recalls or [])
	}

	new_recalls = []
	for alert in alerts:
		recall_id = alert.get("recall_id")
		if not recall_id:
			continue

		# Skip duplicates
		if recall_id in existing_ids:
			continue

		# Match by category + brand (case-insensitive)
		alert_category = (alert.get("category") or "").lower()
		alert_brand = (alert.get("brand") or "").lower()

		category_match = (
			item_category
			and alert_category
			and alert_category in item_category
			or item_category in alert_category
		) if item_category and alert_category else False

		brand_match = (
			item_brand
			and alert_brand
			and (
				alert_brand in item_brand
				or item_brand in alert_brand
			)
		) if item_brand and alert_brand else False

		if not (category_match and brand_match):
			continue

		# Validate severity
		severity = alert.get("severity", "Unknown")
		if severity not in ("Serious", "High", "Medium", "Unknown"):
			severity = "Unknown"

		# Add child row
		item_doc.append("recalls", {
			"recall_id": recall_id,
			"title": alert.get("title") or "",
			"category": alert.get("category") or "",
			"brand": alert.get("brand") or "",
			"severity": severity,
			"published_date": alert.get("published_date"),
			"detail_url": alert.get("detail_url") or "",
			"dismissed": 0,
		})

		existing_ids.add(recall_id)
		new_recalls.append({
			"recall_id": recall_id,
			"title": alert.get("title") or "",
			"severity": severity,
			"detail_url": alert.get("detail_url") or "",
		})

	return new_recalls


def _fetch_eu_safety_gate_alerts(category: str, brand: str) -> list[dict]:
	"""Fetch recall alerts from the EU Safety Gate (RAPEX) API.

	Currently stubbed — returns an empty list. When implemented, this will
	query the EU Safety Gate API for recent alerts matching the given
	category and brand.

	Args:
		category: Appliance category (e.g. "White Goods").
		brand: Appliance brand (e.g. "Bosch").

	Returns:
		list of alert dicts with keys: recall_id, title, category, brand,
		severity, published_date, detail_url.
	"""
	# TODO: implement EU Safety Gate API integration
	return []
