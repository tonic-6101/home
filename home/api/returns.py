# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Purchase Returns API — Feature 18.

Endpoints for listing, retrieving, creating, and updating purchase
return records.  Entirely hidden from Child role.
"""

import frappe
from frappe import _
from frappe.utils import date_diff, today

from home.api.permission import (
	require_household_access,
	require_role,
)

_VALID_RETURN_REASONS = (
	"Defective",
	"Wrong Item",
	"Changed Mind",
	"Damaged in Delivery",
	"Other",
)

_VALID_REFUND_STATUSES = (
	"Pending",
	"Received",
	"Partially Received",
	"Denied",
)


@frappe.whitelist()
def get_returns(property: str) -> dict:
	"""Return all purchase returns for a property with computed overdue flag.

	Entire feature is restricted to Owner/Adult — Child sees nothing.

	Args:
		property: Name of the Home Property record.

	Returns:
		dict with "returns" list ordered by return_date desc.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	returns = frappe.get_all(
		"Home Purchase Return",
		filters={"property": property},
		fields=[
			"name",
			"item_description",
			"retailer",
			"return_date",
			"return_reason",
			"refund_status",
			"refund_expected",
			"refund_amount_received",
			"refund_received_date",
			"linked_item",
		],
		order_by="return_date desc",
	)

	_today = today()
	for r in returns:
		r["days_since_return"] = date_diff(_today, r["return_date"])
		r["overdue_followup"] = (
			r["refund_status"] == "Pending" and r["days_since_return"] > 14
		)

	return {"returns": returns}


@frappe.whitelist()
def get_return(name: str) -> dict:
	"""Return full detail of a purchase return record.

	Args:
		name: Name of the Home Purchase Return record.

	Returns:
		dict with all fields plus days_since_return and overdue_followup.
	"""
	doc = frappe.get_doc("Home Purchase Return", name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	result = doc.as_dict()
	result["days_since_return"] = date_diff(today(), doc.return_date)
	result["overdue_followup"] = (
		doc.refund_status == "Pending" and result["days_since_return"] > 14
	)

	return result


@frappe.whitelist()
def create_return(
	property: str,
	item_description: str,
	return_date: str,
	return_reason: str,
	refund_status: str = "Pending",
	retailer: str = "",
	purchase_date: str | None = None,
	purchase_price: float | None = None,
	refund_expected: float | None = None,
	return_notes: str = "",
	linked_item: str | None = None,
	receipt: str | None = None,
) -> dict:
	"""Create a purchase return record. Owner/Adult only.

	Args:
		property: Name of the Home Property record.
		item_description: What was returned.
		return_date: When the item was returned.
		return_reason: One of Defective / Wrong Item / Changed Mind /
		               Damaged in Delivery / Other.
		refund_status: Pending / Received / Partially Received / Denied.
		retailer: Where it was purchased from.
		purchase_date: Original purchase date.
		purchase_price: Original purchase price.
		refund_expected: How much is expected back.
		return_notes: Additional details.
		linked_item: Optional linked Home Item.
		receipt: Attached receipt file URL.

	Returns:
		dict with "purchase_return" name.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	if return_reason not in _VALID_RETURN_REASONS:
		frappe.throw(
			_("Return reason must be one of: {0}").format(
				", ".join(_VALID_RETURN_REASONS)
			)
		)

	if refund_status not in _VALID_REFUND_STATUSES:
		frappe.throw(
			_("Refund status must be one of: {0}").format(
				", ".join(_VALID_REFUND_STATUSES)
			)
		)

	doc = frappe.get_doc(
		{
			"doctype": "Home Purchase Return",
			"property": property,
			"item_description": item_description,
			"return_date": return_date,
			"return_reason": return_reason,
			"refund_status": refund_status,
			"retailer": retailer,
			"purchase_date": purchase_date,
			"purchase_price": purchase_price,
			"refund_expected": refund_expected,
			"return_notes": return_notes,
			"linked_item": linked_item,
			"receipt": receipt,
		}
	).insert()

	return {"purchase_return": doc.name}


@frappe.whitelist()
def mark_refund_received(
	name: str,
	refund_amount_received: float,
	refund_received_date: str | None = None,
) -> dict:
	"""Mark a pending return as refund received. Owner/Adult only.

	Args:
		name: Name of the Home Purchase Return record.
		refund_amount_received: Actual amount received.
		refund_received_date: Date refund arrived (defaults to today).

	Returns:
		dict with updated record name and status.
	"""
	doc = frappe.get_doc("Home Purchase Return", name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	doc.refund_amount_received = refund_amount_received
	doc.refund_received_date = refund_received_date or today()

	if (
		doc.refund_expected
		and refund_amount_received < doc.refund_expected
	):
		doc.refund_status = "Partially Received"
	else:
		doc.refund_status = "Received"

	doc.save()

	return {
		"purchase_return": doc.name,
		"refund_status": doc.refund_status,
	}


@frappe.whitelist()
def update_return(name: str, **kwargs) -> dict:
	"""Update fields on a purchase return. Owner/Adult only.

	Args:
		name: Name of the Home Purchase Return record.
		**kwargs: Fields to update.

	Returns:
		dict with updated record name.
	"""
	doc = frappe.get_doc("Home Purchase Return", name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	allowed_fields = {
		"item_description",
		"retailer",
		"purchase_date",
		"purchase_price",
		"return_date",
		"return_reason",
		"return_notes",
		"refund_expected",
		"refund_status",
		"refund_amount_received",
		"refund_received_date",
		"linked_item",
		"receipt",
	}

	for field, value in kwargs.items():
		if field in allowed_fields:
			if field == "return_reason" and value not in _VALID_RETURN_REASONS:
				frappe.throw(
					_("Return reason must be one of: {0}").format(
						", ".join(_VALID_RETURN_REASONS)
					)
				)
			if field == "refund_status" and value not in _VALID_REFUND_STATUSES:
				frappe.throw(
					_("Refund status must be one of: {0}").format(
						", ".join(_VALID_REFUND_STATUSES)
					)
				)
			setattr(doc, field, value)

	doc.save()
	return {"purchase_return": doc.name}
