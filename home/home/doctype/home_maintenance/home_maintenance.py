# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import add_days, add_months


RECURRENCE_MAP = {
	"Weekly": lambda d: add_days(d, 7),
	"Bi-weekly": lambda d: add_days(d, 14),
	"Monthly": lambda d: add_months(d, 1),
	"Quarterly": lambda d: add_months(d, 3),
	"Bi-annual": lambda d: add_months(d, 6),
	"Annual": lambda d: add_months(d, 12),
}


class HomeMaintenance(Document):
	def before_save(self):
		self._fetch_household()

	def on_update(self):
		if (
			self.has_value_changed("status")
			and self.status == "Completed"
			and self.maintenance_type == "Recurring"
			and self.recurrence
			and self.completed_date
		):
			self._create_next_occurrence()

	def _fetch_household(self):
		"""Auto-fetch household from the linked property."""
		if self.property:
			self.household = frappe.db.get_value(
				"Home Property", self.property, "household"
			)

	def _create_next_occurrence(self):
		"""Create the next recurring maintenance task based on RECURRENCE_MAP."""
		calc_fn = RECURRENCE_MAP.get(self.recurrence)
		if not calc_fn:
			return

		next_date = calc_fn(self.completed_date)

		next_task = frappe.copy_doc(self)
		next_task.status = "Scheduled"
		next_task.scheduled_date = next_date
		next_task.completed_date = None
		next_task.cost = None
		next_task.notes = None
		next_task.insert(ignore_permissions=True)

		frappe.msgprint(
			_("Next recurring task {0} created for {1}").format(
				next_task.name, next_date
			),
			alert=True,
		)
