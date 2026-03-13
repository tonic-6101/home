# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.model.document import Document


class HomeInventoryItem(Document):
	def before_save(self):
		self._fetch_household()

	def _fetch_household(self):
		"""Auto-fetch household from the linked property."""
		if self.property:
			self.household = frappe.db.get_value(
				"Home Property", self.property, "household"
			)
