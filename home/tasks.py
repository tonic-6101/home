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
	"""Daily task: notify household owners of warranties expiring soon.

	Two configurable thresholds per household (defaults: 90 and 30 days).
	Delivered via Dock notification if installed, email fallback.
	"""
	warranties = frappe.get_all(
		"Home Warranty",
		filters={
			"end_date": [">=", today()],
		},
		fields=["name", "appliance", "end_date", "household", "property"],
	)

	for warranty in warranties:
		days_left = (
			frappe.utils.getdate(warranty.end_date) - frappe.utils.getdate(today())
		).days

		thresholds = _get_alert_thresholds(warranty.household)
		if days_left not in (thresholds["alert_1"], thresholds["alert_2"]):
			# Only notify on exact threshold days to avoid spam
			if days_left > thresholds["alert_1"]:
				continue
			if days_left > thresholds["alert_2"] and days_left < thresholds["alert_1"]:
				continue

		members = _get_household_owners(warranty.household)
		for user in members:
			_send_notification(
				user=user,
				title=_("Warranty expiring soon"),
				message=_("Warranty for {0} expires on {1} ({2} days left)").format(
					warranty.appliance, warranty.end_date, days_left
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
			"status": "Scheduled",
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

		members = _get_household_owners(task.household)
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
