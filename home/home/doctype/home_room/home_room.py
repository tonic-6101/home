# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.model.document import Document


class HomeRoom(Document):
	def before_insert(self):
		if self.property:
			from home.api.permission import require_property_not_archived

			require_property_not_archived(self.property)

	def before_save(self):
		self._fetch_household()

	def on_trash(self):
		self._unlink_items()

	def _fetch_household(self):
		"""Auto-fetch household from the linked property."""
		if self.property:
			self.household = frappe.db.get_value("Home Property", self.property, "household")

	def _unlink_items(self):
		"""Nullify room reference on linked items."""
		frappe.db.set_value(
			"Home Item",
			{"room": self.name},
			"room",
			None,
			update_modified=False,
		)
