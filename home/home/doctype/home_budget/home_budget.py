# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomeBudget(Document):
	def before_insert(self):
		if self.property:
			from home.api.permission import require_property_not_archived

			require_property_not_archived(self.property)

	def before_save(self):
		if self.property:
			self.household = frappe.db.get_value("Home Property", self.property, "household")

	def validate(self):
		existing = frappe.get_all(
			"Home Budget",
			filters={
				"property": self.property,
				"budget_year": self.budget_year,
				"name": ["!=", self.name],
			},
			limit=1,
		)
		if existing:
			frappe.throw(
				_("A budget already exists for this property and year ({0})").format(self.budget_year)
			)
