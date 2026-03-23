# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Home Settings API (Feature 38).

Provides endpoints for reading and updating per-household settings,
including alert thresholds, appliance category lifespans, default
currency, and financial visibility.  Settings are lazily initialized
with defaults when first accessed.
"""

import frappe
from frappe import _

from home.api.permission import require_household_access, require_role

# Default threshold values for lazy initialization
_DEFAULTS = {
	"warranty_alert_days_1": 90,
	"warranty_alert_days_2": 30,
	"maintenance_reminder_days": 3,
	"refund_overdue_days": 14,
	"insurance_renewal_days": 60,
	"financial_visibility": "Owner and Adult",
}

# Scalar fields that can be updated via save_settings
_ALLOWED_FIELDS = {
	"warranty_alert_days_1",
	"warranty_alert_days_2",
	"maintenance_reminder_days",
	"refund_overdue_days",
	"insurance_renewal_days",
	"default_currency",
	"financial_visibility",
}

# Default category lifespan seed data
_DEFAULT_LIFESPANS = [
	{"category": "White Goods", "lifespan_years": 12, "avg_replacement_cost": 600},
	{"category": "HVAC", "lifespan_years": 15, "avg_replacement_cost": 2500},
	{"category": "Heating", "lifespan_years": 20, "avg_replacement_cost": 3000},
	{"category": "Electronics", "lifespan_years": 7, "avg_replacement_cost": 400},
	{"category": "Kitchen", "lifespan_years": 10, "avg_replacement_cost": 350},
	{"category": "Plumbing", "lifespan_years": 25, "avg_replacement_cost": 800},
	{"category": "Other", "lifespan_years": 10, "avg_replacement_cost": 500},
]


@frappe.whitelist()
def get_settings(household: str) -> dict:
	"""Return the Home Settings record for the household.

	Owner-only.  If no settings record exists yet, creates one with
	default values (lazy initialization).

	Args:
		household: Name of the Home Household record.

	Returns:
		dict with the settings fields and category_lifespans table.
	"""
	require_household_access(household)
	require_role(household, "Owner")

	settings = _get_or_create_settings(household)

	lifespans = [
		{
			"category": row.category,
			"lifespan_years": row.lifespan_years,
			"avg_replacement_cost": row.avg_replacement_cost,
		}
		for row in settings.lifespan_defaults
	]

	return {
		"name": settings.name,
		"household": settings.household,
		"warranty_alert_days_1": settings.warranty_alert_days_1,
		"warranty_alert_days_2": settings.warranty_alert_days_2,
		"maintenance_reminder_days": settings.maintenance_reminder_days,
		"refund_overdue_days": settings.refund_overdue_days,
		"insurance_renewal_days": settings.insurance_renewal_days,
		"default_currency": settings.default_currency,
		"financial_visibility": settings.financial_visibility,
		"category_lifespans": lifespans,
	}


@frappe.whitelist()
def save_settings(household: str, **kwargs) -> dict:
	"""Update settings fields for the household.

	Only the household Owner can save settings.  Accepts scalar fields
	and an optional ``category_lifespans`` list to replace the lifespan
	child table.

	Args:
		household: Name of the Home Household record.
		**kwargs: Settings fields to update.  ``category_lifespans``
			should be a list of dicts with ``category``,
			``lifespan_years``, and ``avg_replacement_cost``.

	Returns:
		dict confirming the update with the settings name.
	"""
	require_household_access(household)
	require_role(household, "Owner")

	settings = _get_or_create_settings(household)

	updated_fields = []
	for field, value in kwargs.items():
		if field in _ALLOWED_FIELDS:
			setattr(settings, field, value)
			updated_fields.append(field)

	# Handle category_lifespans child table replacement
	lifespans = kwargs.get("category_lifespans")
	if lifespans is not None:
		if isinstance(lifespans, str):
			import json

			lifespans = json.loads(lifespans)

		settings.lifespan_defaults = []
		for row in lifespans:
			settings.append(
				"lifespan_defaults",
				{
					"category": row["category"],
					"lifespan_years": row.get("lifespan_years"),
					"avg_replacement_cost": row.get("avg_replacement_cost"),
				},
			)
		updated_fields.append("category_lifespans")

	if not updated_fields:
		frappe.throw(_("No valid fields provided to update"))

	settings.save(ignore_permissions=True)

	return {
		"settings": settings.name,
		"updated_fields": updated_fields,
	}


@frappe.whitelist()
def reset_onboarding(household: str) -> dict:
	"""Reset onboarding_tour_completed to 0 for all household members.

	Only the household Owner can reset onboarding.

	Args:
		household: Name of the Home Household record.

	Returns:
		dict with the count of members reset.
	"""
	require_household_access(household)
	require_role(household, "Owner")

	household_doc = frappe.get_doc("Home Household", household)
	reset_count = 0

	for member in household_doc.members:
		if member.onboarding_tour_completed:
			member.onboarding_tour_completed = 0
			reset_count += 1

	if reset_count:
		household_doc.save(ignore_permissions=True)

	return {"members_reset": reset_count}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_or_create_settings(household: str):
	"""Return existing Home Settings for the household, or create with defaults."""
	existing = frappe.get_all(
		"Home Settings",
		filters={"household": household},
		fields=["name"],
		limit=1,
	)

	if existing:
		return frappe.get_doc("Home Settings", existing[0].name)

	settings = frappe.new_doc("Home Settings")
	settings.household = household

	for field, default in _DEFAULTS.items():
		setattr(settings, field, default)

	settings.default_currency = frappe.db.get_default("currency") or "EUR"

	for row in _DEFAULT_LIFESPANS:
		settings.append("lifespan_defaults", row)

	settings.insert(ignore_permissions=True)
	return settings
