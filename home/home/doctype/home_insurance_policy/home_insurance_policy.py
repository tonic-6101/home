# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomeInsurancePolicy(Document):
	def before_insert(self):
		if self.property:
			from home.api.permission import require_property_not_archived

			require_property_not_archived(self.property)

	def before_save(self):
		if self.property:
			self.household = frappe.db.get_value("Home Property", self.property, "household")

		if not self.renewal_notice_days:
			self.renewal_notice_days = 60

	def validate(self):
		if self.start_date and self.end_date and self.start_date >= self.end_date:
			frappe.throw(_("Start date must be before end date"))
