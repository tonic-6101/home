# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Scheduled tasks for Home.

Registered in hooks.py under scheduler_events → daily.
"""

import frappe
from frappe import _
from frappe.utils import add_days, today

from home.api.utils import _send_notification


def send_warranty_expiry_alerts() -> None:
	"""Daily task: notify household owners and adults of warranties expiring soon.

	Two configurable thresholds per household (defaults: 90 and 30 days).
	Each threshold fires exactly once per warranty — we check for an exact-day
	match (end_date == today + N), so no "already sent" flag is needed.
	Delivered via Dock notification if installed, email fallback.
	"""
	warranties = frappe.get_all(
		"Home Warranty",
		filters={"end_date": [">=", today()]},
		fields=["name", "item", "end_date", "household"],
	)

	# Cache thresholds per household to avoid repeated DB lookups
	threshold_cache: dict[str, dict] = {}

	for warranty in warranties:
		hh = warranty.household
		if hh not in threshold_cache:
			threshold_cache[hh] = _get_alert_thresholds(hh)

		thresholds = threshold_cache[hh]
		days_left = (
			frappe.utils.getdate(warranty.end_date) - frappe.utils.getdate(today())
		).days

		# Exact-day match only — fires once per threshold crossing
		if days_left not in (thresholds["alert_1"], thresholds["alert_2"]):
			continue

		members = _get_household_adults(warranty.household)
		for user in members:
			_send_notification(
				user=user,
				title=_("Warranty expiring in {0} days").format(days_left),
				message=_("Warranty for {0} expires on {1}.").format(
					warranty.item, warranty.end_date
				),
				source_doctype="Home Warranty",
				source_name=warranty.name,
				notification_type="warranty_expiring",
			)


def send_maintenance_reminders() -> None:
	"""Daily task: remind household members of upcoming scheduled maintenance.

	Sends a reminder N days before the scheduled date (default: 3 days).
	"""
	default_reminder_days = 3

	upcoming = frappe.get_all(
		"Home Maintenance",
		filters={
			"status": ["in", ["Scheduled", "In Progress"]],
			"scheduled_date": ["between", [today(), add_days(today(), 30)]],
		},
		fields=["name", "title", "scheduled_date", "household", "property"],
	)

	for task in upcoming:
		days_until = (
			frappe.utils.getdate(task.scheduled_date) - frappe.utils.getdate(today())
		).days

		reminder_days = _get_reminder_days(task.household) or default_reminder_days
		if days_until != reminder_days:
			continue

		members = _get_household_adults(task.household)
		for user in members:
			_send_notification(
				user=user,
				title=_("Maintenance due soon"),
				message=_("{0} is scheduled for {1} ({2} days from now)").format(
					task.title, task.scheduled_date, days_until
				),
				source_doctype="Home Maintenance",
				source_name=task.name,
				notification_type="maintenance_due",
			)


def send_insurance_renewal_alerts() -> None:
	"""Daily task: notify household members of insurance policies due for renewal.

	Each policy has its own renewal_notice_days (default 60).
	Fires on the exact day the window opens.
	"""
	policies = frappe.get_all(
		"Home Insurance Policy",
		filters={"end_date": [">=", today()]},
		fields=[
			"name", "policy_name", "provider", "end_date",
			"renewal_notice_days", "auto_renews", "household", "property",
		],
	)

	_today = today()
	for policy in policies:
		days = policy.get("renewal_notice_days") or 60
		target_date = add_days(_today, days)
		if str(policy["end_date"]) != str(target_date):
			continue

		auto = _("auto-renews") if policy.get("auto_renews") else _("requires manual renewal")
		message = _("{0} ({1}) renews in {2} days — {3}.").format(
			policy["policy_name"], policy["provider"], days, auto
		)

		members = _get_household_adults(policy["household"])
		for user in members:
			_send_notification(
				user=user,
				title=_("Insurance renewal in {0} days").format(days),
				message=message,
				source_doctype="Home Insurance Policy",
				source_name=policy["name"],
				notification_type="insurance_renewal",
			)


def send_unpaid_bill_reminders() -> None:
	"""Daily task: notify household members of utility bills due soon.

	Uses configurable ``maintenance_reminder_days`` threshold from Home Settings
	(default: 3 days).
	"""
	# Gather all unpaid bills with a due date in the near future
	upcoming = frappe.get_all(
		"Home Utility Bill",
		filters={
			"paid": 0,
			"due_date": ["between", [today(), add_days(today(), 30)]],
		},
		fields=["name", "bill_type", "amount", "due_date", "household", "property"],
	)

	reminder_cache: dict[str, int] = {}
	due_soon = []
	for bill in upcoming:
		hh = bill["household"]
		if hh not in reminder_cache:
			reminder_cache[hh] = _get_reminder_days(hh) or 3
		days_until = (
			frappe.utils.getdate(bill["due_date"]) - frappe.utils.getdate(today())
		).days
		if days_until == reminder_cache[hh]:
			due_soon.append(bill)

	for bill in due_soon:
		message = _("{0} bill of {1} is due on {2}").format(
			bill["bill_type"],
			frappe.format_value(bill["amount"], {"fieldtype": "Currency"}),
			bill["due_date"],
		)

		members = _get_household_adults(bill["household"])
		for user in members:
			_send_notification(
				user=user,
				title=_("Utility bill due soon"),
				message=message,
				source_doctype="Home Utility Bill",
				source_name=bill["name"],
				notification_type="bill_due",
			)


def send_overdue_refund_alerts() -> None:
	"""Daily task: notify household members of overdue purchase return refunds.

	First alert at configurable ``refund_overdue_days`` (default 14),
	then every 7 days until resolved.
	"""
	from frappe.utils import date_diff

	from home.home.doctype.home_settings.home_settings import get_threshold

	pending = frappe.get_all(
		"Home Purchase Return",
		filters={
			"refund_status": "Pending",
		},
		fields=["name", "item_description", "return_date", "refund_expected", "household"],
	)

	_today = today()
	threshold_cache: dict[str, int] = {}
	for ret in pending:
		hh = ret["household"]
		if hh not in threshold_cache:
			threshold_cache[hh] = get_threshold(hh, "refund_overdue_days") or 14

		overdue_days = threshold_cache[hh]
		days_since = date_diff(_today, ret["return_date"])
		if days_since < overdue_days:
			continue
		# Fire at overdue_days, then every 7 days
		if days_since == overdue_days or (days_since > overdue_days and (days_since - overdue_days) % 7 == 0):
			message = _("Refund for '{0}' has been pending for {1} days").format(
				ret["item_description"], days_since
			)

			members = _get_household_adults(ret["household"])
			for user in members:
				_send_notification(
					user=user,
					title=_("Overdue refund"),
					message=message,
					source_doctype="Home Purchase Return",
					source_name=ret["name"],
					notification_type="refund_overdue",
				)


def check_item_recalls() -> None:
	"""Weekly task: check EU Safety Gate (RAPEX) for item recalls.

	Downloads the RAPEX alert feed and matches against registered items
	by category and brand. Creates Home Item Recall child rows for matches.
	Feed fetch failures are silent (logged only).
	"""
	alerts = _fetch_safety_gate_alerts()
	if not alerts:
		return

	items = frappe.get_all(
		"Home Item",
		filters={"item_type": "Appliance", "status": ["!=", "Disposed"]},
		fields=["name", "category", "brand", "household"],
	)

	for item in items:
		if not item.brand:
			continue

		matches = _match_item_recalls(item, alerts)
		if matches:
			doc = frappe.get_doc("Home Item", item.name)
			existing_ids = {r.recall_id for r in doc.recalls}
			new_matches = [m for m in matches if m["recall_id"] not in existing_ids]

			for match in new_matches:
				doc.append("recalls", match)

			doc.last_recall_check = today()
			doc.save(ignore_permissions=True)

			if new_matches:
				members = _get_household_adults(item.household)
				for user in members:
					_send_notification(
						user=user,
						title=_("Item recall alert"),
						message=_("A recall may affect your {0}. Check the item page for details.").format(
							item.name
						),
						source_doctype="Home Item",
						source_name=item.name,
						notification_type="recall_alert",
					)
		else:
			frappe.db.set_value(
				"Home Item", item.name,
				"last_recall_check", today(),
				update_modified=False,
			)


def send_equity_update_reminders() -> None:
	"""Annual task: nudge owners to update property value and mortgage balance.

	Fires when estimated_value_date is more than 11 months ago.
	"""
	from frappe.utils import add_months

	cutoff = str(add_months(today(), -11))

	properties = frappe.get_all(
		"Home Property",
		filters={
			"ownership_status": "Owner-occupied",
			"is_archived": 0,
		},
		fields=["name", "property_name", "household", "estimated_value_date"],
	)

	for prop in properties:
		val_date = prop.get("estimated_value_date")
		if not val_date or str(val_date) < cutoff:
			message = _(
				"It has been over a year since you updated the estimated value for {0}. "
				"Update it to keep your equity figure current."
			).format(prop["property_name"])

			members = _get_household_owners(prop["household"])
			for user in members:
				_send_notification(
					user=user,
					title=_("Update your home equity figures"),
					message=message,
					source_doctype="Home Property",
					source_name=prop["name"],
					notification_type="equity_update",
				)


# -- Internal helpers --


def _get_alert_thresholds(household: str) -> dict:
	"""Get warranty alert thresholds for a household from Home Settings."""
	settings = frappe.db.get_value(
		"Home Settings",
		{"household": household},
		["warranty_alert_days_1", "warranty_alert_days_2"],
		as_dict=True,
	)
	return {
		"alert_1": (settings and settings.warranty_alert_days_1) or 90,
		"alert_2": (settings and settings.warranty_alert_days_2) or 30,
	}


def _get_reminder_days(household: str) -> int:
	"""Get maintenance reminder days for a household from Home Settings."""
	val = frappe.db.get_value(
		"Home Settings",
		{"household": household},
		"maintenance_reminder_days",
	)
	return val or 3


def _get_household_owners(household: str) -> list[str]:
	"""Get all users with Owner role in a household."""
	return frappe.get_all(
		"Home Household Member",
		filters={"parent": household, "role": "Owner", "user": ["is", "set"]},
		pluck="user",
	)


def _get_household_adults(household: str) -> list[str]:
	"""Get all users with Owner or Adult role in a household."""
	return frappe.get_all(
		"Home Household Member",
		filters={
			"parent": household,
			"role": ["in", ["Owner", "Adult"]],
			"user": ["is", "set"],
		},
		pluck="user",
	)


def _fetch_safety_gate_alerts() -> list[dict]:
	"""Fetch alerts from EU Safety Gate (RAPEX).

	Stub — returns empty list. In production, queries the EU Safety Gate
	REST API and returns parsed alert dicts.
	"""
	# In production:
	# try:
	#     response = requests.get(SAFETY_GATE_URL, timeout=30)
	#     return _parse_safety_gate_response(response.json())
	# except Exception:
	#     frappe.log_error("Safety Gate fetch failed")
	#     return []
	return []


def _match_item_recalls(item: dict, alerts: list[dict]) -> list[dict]:
	"""Match alerts against an item by category + brand (case-insensitive)."""
	matches = []
	brand = (item.get("brand") or "").lower()
	category = (item.get("category") or "").lower()

	if not brand:
		return matches

	for alert in alerts:
		alert_brand = (alert.get("brand") or "").lower()
		alert_category = (alert.get("category") or "").lower()

		if brand in alert_brand and category in alert_category:
			matches.append({
				"recall_id": alert["recall_id"],
				"title": alert.get("title", ""),
				"category": alert.get("category", ""),
				"brand": alert.get("brand", ""),
				"severity": alert.get("severity", "Unknown"),
				"published_date": alert.get("published_date"),
				"detail_url": alert.get("detail_url", ""),
			})

	return matches
