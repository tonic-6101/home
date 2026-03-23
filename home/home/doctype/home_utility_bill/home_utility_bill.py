# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, today


class HomeUtilityBill(Document):
	def before_insert(self):
		if self.property:
			from home.api.permission import require_property_not_archived

			require_property_not_archived(self.property)

	def before_save(self):
		if self.property:
			self.household = frappe.db.get_value("Home Property", self.property, "household")

		# Auto-compute consumption from meter readings (overrides direct entry)
		if self.reading_start and self.reading_end:
			self.consumption_amount = self.reading_end - self.reading_start

		# Default consumption_unit based on bill_type
		if self.consumption_amount and not self.consumption_unit:
			self.consumption_unit = _default_consumption_unit(self.bill_type)

		# Auto-set paid_date when marking as paid
		if self.paid and not self.paid_date:
			self.paid_date = today()

	def after_insert(self):
		self._check_cost_spike()

	def _check_cost_spike(self):
		"""Warn if this bill is >150% of the 12-month average for the same bill type."""
		avg = frappe.db.get_value(
			"Home Utility Bill",
			{
				"property": self.property,
				"bill_type": self.bill_type,
				"period_start": [">=", add_months(today(), -12)],
				"name": ["!=", self.name],
			},
			"avg(amount)",
		)
		if avg and self.amount > avg * 1.5:
			pct = round((self.amount / avg - 1) * 100)
			frappe.msgprint(
				_("This bill is {0}% higher than your usual {1} spend. 12-month average: {2}").format(
					pct, self.bill_type, frappe.format_value(avg, {"fieldtype": "Currency"})
				),
				title=_("Cost Spike Detected"),
				indicator="orange",
			)


_DEFAULT_UNIT = {
	"Electricity": "kWh",
	"Gas": "m³",
	"Water": "m³",
	"Heating Oil": "Litres",
	"District Heating": "kWh",
}


def _default_consumption_unit(bill_type: str) -> str | None:
	"""Return the default consumption unit for a given bill type."""
	return _DEFAULT_UNIT.get(bill_type)
