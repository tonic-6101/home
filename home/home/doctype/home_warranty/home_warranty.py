# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomeWarranty(Document):
	def before_save(self):
		self._fetch_property_and_household()

	def validate(self):
		self._validate_dates()

	def _fetch_property_and_household(self):
		"""Auto-fetch property from appliance, household from property."""
		if self.appliance:
			appliance = frappe.db.get_value(
				"Home Appliance", self.appliance, ["property"], as_dict=True
			)
			if appliance:
				self.property = appliance.property

		if self.property:
			self.household = frappe.db.get_value(
				"Home Property", self.property, "household"
			)

	def _validate_dates(self):
		"""Ensure start_date is before end_date."""
		if self.start_date and self.end_date and self.start_date >= self.end_date:
			frappe.throw(_("Start Date must be before End Date"))
