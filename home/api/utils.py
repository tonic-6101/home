# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _


def _send_notification(
	*,
	user: str,
	title: str,
	message: str,
	source_doctype: str | None = None,
	source_name: str | None = None,
	notification_type: str = "maintenance_due",
) -> None:
	"""Send a notification via Dock if installed, otherwise fall back to email.

	This is the single notification entry point for all Home alerts
	(warranty expiry, maintenance reminders, overdue refunds, etc.).
	"""
	if "dock" in frappe.get_installed_apps():
		frappe.get_doc(
			{
				"doctype": "Dock Notification",
				"source_app": "home",
				"source_doctype": source_doctype,
				"source_name": source_name,
				"notification_type": notification_type,
				"title": title,
				"message": message,
				"user": user,
			}
		).insert(ignore_permissions=True)
	else:
		frappe.sendmail(
			recipients=[user],
			subject=title,
			message=message,
		)
