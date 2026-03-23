# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Insurance policy APIs (Features 28–29)."""

import frappe
from frappe import _
from frappe.utils import date_diff, today

from home.api.permission import require_household_access, require_role

_VALID_POLICY_TYPES = (
	"Buildings",
	"Contents",
	"Liability",
	"Legal Protection",
	"Flood",
	"Other",
)

_VALID_CLAIM_OUTCOMES = ("Pending", "Approved", "Partial", "Rejected")


@frappe.whitelist()
def get_policies(property: str) -> dict:
	"""Return insurance policies for a property with computed renewal status.

	Hidden from Child role — requires Adult or Owner.
	"""
	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	policies = frappe.get_all(
		"Home Insurance Policy",
		filters={"property": property},
		fields=[
			"name",
			"policy_name",
			"policy_type",
			"provider",
			"policy_number",
			"start_date",
			"end_date",
			"premium_annual",
			"coverage_amount",
			"auto_renews",
			"renewal_notice_days",
			"document",
		],
		order_by="end_date asc",
	)

	_today = today()
	for p in policies:
		days_left = date_diff(p["end_date"], _today)
		notice = p.get("renewal_notice_days") or 60
		if days_left < 0:
			p["renewal_status"] = "expired"
		elif days_left <= notice:
			p["renewal_status"] = "renewing_soon"
		else:
			p["renewal_status"] = "active"
		p["days_to_renewal"] = max(days_left, 0)

	total_annual_premium = sum(p.get("premium_annual") or 0 for p in policies)

	return {
		"policies": policies,
		"total_annual_premium": total_annual_premium,
	}


@frappe.whitelist()
def get_policy(name: str) -> dict:
	"""Return full insurance policy detail including claims.

	Hidden from Child role — requires Adult or Owner.
	"""
	doc = frappe.get_doc("Home Insurance Policy", name)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	result = doc.as_dict()

	# Add computed renewal status
	_today = today()
	days_left = date_diff(doc.end_date, _today)
	notice = doc.renewal_notice_days or 60
	if days_left < 0:
		result["renewal_status"] = "expired"
	elif days_left <= notice:
		result["renewal_status"] = "renewing_soon"
	else:
		result["renewal_status"] = "active"
	result["days_to_renewal"] = max(days_left, 0)

	return result


@frappe.whitelist()
def create_policy(
	property: str,
	policy_name: str,
	policy_type: str,
	provider: str,
	start_date: str,
	end_date: str,
	policy_number: str = "",
	premium_annual: float | None = None,
	coverage_amount: float | None = None,
	coverage_notes: str = "",
	auto_renews: bool = False,
	renewal_notice_days: int = 60,
	notes: str = "",
	document: str | None = None,
) -> dict:
	"""Create a new insurance policy. Owner/Adult only.

	Args:
		property: Name of the Home Property record.
		policy_name: Display name for the policy.
		policy_type: One of Buildings / Contents / Liability / Legal Protection /
		             Flood / Other.
		provider: Insurance company name.
		start_date: Policy start date.
		end_date: Renewal / expiry date.
		policy_number: Policy reference number.
		premium_annual: Annual premium amount.
		coverage_amount: Sum insured.
		coverage_notes: Key inclusions, exclusions, deductibles.
		auto_renews: Whether policy auto-renews.
		renewal_notice_days: Days before end_date to send alert.
		notes: Additional notes.
		document: Attached policy PDF URL.

	Returns:
		dict with "insurance_policy" name.
	"""
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	if policy_type not in _VALID_POLICY_TYPES:
		frappe.throw(
			_("Policy type must be one of: {0}").format(
				", ".join(_VALID_POLICY_TYPES)
			)
		)

	doc = frappe.get_doc(
		{
			"doctype": "Home Insurance Policy",
			"property": property,
			"policy_name": policy_name,
			"policy_type": policy_type,
			"provider": provider,
			"start_date": start_date,
			"end_date": end_date,
			"policy_number": policy_number,
			"premium_annual": premium_annual,
			"coverage_amount": coverage_amount,
			"coverage_notes": coverage_notes,
			"auto_renews": auto_renews,
			"renewal_notice_days": renewal_notice_days or 60,
			"notes": notes,
			"document": document,
		}
	).insert()

	return {"insurance_policy": doc.name}


@frappe.whitelist()
def add_claim(
	policy: str,
	claim_date: str,
	incident_description: str,
	outcome: str = "Pending",
	claim_amount: float = 0,
	payout_amount: float = 0,
	notes: str = "",
) -> dict:
	"""Add a claim to an insurance policy. Owner/Adult only.

	Args:
		policy: Name of the Home Insurance Policy record.
		claim_date: Date the claim was submitted.
		incident_description: What happened.
		outcome: Pending / Approved / Partial / Rejected.
		claim_amount: Amount claimed.
		payout_amount: Amount paid out.
		notes: Reference numbers, loss adjuster notes.

	Returns:
		dict with policy name and new claim idx.
	"""
	doc = frappe.get_doc("Home Insurance Policy", policy)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	if outcome not in _VALID_CLAIM_OUTCOMES:
		frappe.throw(
			_("Outcome must be one of: {0}").format(
				", ".join(_VALID_CLAIM_OUTCOMES)
			)
		)

	row = doc.append("claims", {
		"claim_date": claim_date,
		"incident_description": incident_description,
		"outcome": outcome,
		"claim_amount": claim_amount,
		"payout_amount": payout_amount,
		"notes": notes,
	})
	doc.save()

	return {
		"policy": doc.name,
		"claim_idx": row.idx,
		"claim_name": row.name,
	}
