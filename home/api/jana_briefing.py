# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Tonic

"""Jana Daily Briefing source — Home household management data."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, getdate, nowdate


@frappe.whitelist()
def get_briefing(date: str | None = None) -> dict:
	"""Return a briefing summary of household management data.

	Includes expiring warranties, and overdue utility bills.
	"""
	today = getdate(date or nowdate())

	return {
		"expiring_warranties": _get_expiring_warranties(today),
		"overdue_bills": _get_overdue_bills(today),
	}


def _get_expiring_warranties(today) -> list[dict]:
	"""Return warranties expiring within the next 30 days."""
	horizon = add_days(today, 30)

	return frappe.get_all(
		"Home Warranty",
		filters={
			"owner": frappe.session.user,
			"end_date": ["between", [today, horizon]],
		},
		fields=["name", "item", "provider", "end_date"],
		order_by="end_date asc",
		limit_page_length=10,
	)


def _get_overdue_bills(today) -> list[dict]:
	"""Return utility bills that are past due and unpaid."""
	return frappe.get_all(
		"Home Utility Bill",
		filters={
			"owner": frappe.session.user,
			"due_date": ["<", today],
			"paid": 0,
		},
		fields=["name", "bill_type", "amount", "due_date", "provider"],
		order_by="due_date asc",
		limit_page_length=10,
	)
