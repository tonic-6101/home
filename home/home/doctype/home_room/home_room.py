# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.model.document import Document


class HomeRoom(Document):
	def before_save(self):
		self._fetch_household()

	def on_trash(self):
		self._unlink_appliances_and_inventory()

	def _fetch_household(self):
		"""Auto-fetch household from the linked property."""
		if self.property:
			self.household = frappe.db.get_value("Home Property", self.property, "household")

	def _unlink_appliances_and_inventory(self):
		"""Nullify room reference on linked appliances and inventory items."""
		for dt in ("Home Appliance", "Home Inventory Item"):
			if frappe.db.exists("DocType", dt):
				frappe.db.set_value(
					dt,
					{"room": self.name},
					"room",
					None,
					update_modified=False,
				)
