# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.model.document import Document


class HomeImprovementWish(Document):
	def before_insert(self):
		if self.property:
			from home.api.permission import require_property_not_archived

			require_property_not_archived(self.property)

	def before_save(self):
		if self.property:
			self.household = frappe.db.get_value("Home Property", self.property, "household")
