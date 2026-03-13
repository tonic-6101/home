# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Home Settings — per-household configuration.

One record per household. Auto-created with defaults when a household is created.
Not a Frappe Single — settings are household-scoped, not site-wide.
"""

import frappe
from frappe import _
from frappe.model.document import Document


class HomeSettings(Document):
	def before_save(self):
		self._apply_defaults()

	def _apply_defaults(self):
		"""Set default values for blank threshold fields."""
		defaults = {
			"warranty_alert_days_1": 90,
			"warranty_alert_days_2": 30,
			"maintenance_reminder_days": 3,
			"refund_overdue_days": 14,
			"insurance_renewal_days": 60,
			"financial_visibility": "Owner and Adult",
		}
		for field, default in defaults.items():
			if not self.get(field):
				self.set(field, default)


def get_threshold(household: str, key: str) -> int:
	"""Return a threshold value for a given key from Home Settings.

	Falls back to system default if no Settings record exists (lazy init).
	"""
	system_defaults = {
		"warranty_alert_days_1": 90,
		"warranty_alert_days_2": 30,
		"maintenance_reminder_days": 3,
		"refund_overdue_days": 14,
		"insurance_renewal_days": 60,
	}

	val = frappe.db.get_value("Home Settings", {"household": household}, key)
	return val or system_defaults.get(key, 0)


def can_see_financial_data(household: str, role: str) -> bool:
	"""Return True if the given household role can see financial data.

	Owner: always True.
	Adult: True when financial_visibility = 'Owner and Adult'.
	Child: always False.
	"""
	if role == "Owner":
		return True
	if role == "Child":
		return False

	visibility = frappe.db.get_value(
		"Home Settings", {"household": household}, "financial_visibility"
	)
	return visibility == "Owner and Adult"
