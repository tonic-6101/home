# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomePurchaseReturn(Document):
	def before_save(self):
		self._fetch_household()

	def on_update(self):
		self._suggest_appliance_disposal()

	def _fetch_household(self):
		"""Auto-fetch household from the linked property."""
		if self.property:
			self.household = frappe.db.get_value(
				"Home Property", self.property, "household"
			)

	def _suggest_appliance_disposal(self):
		"""If linked appliance and reason is Defective, suggest marking it Disposed."""
		if (
			self.linked_appliance
			and self.return_reason == "Defective"
			and self.has_value_changed("return_reason")
		):
			appliance_status = frappe.db.get_value(
				"Home Appliance", self.linked_appliance, "status"
			)
			if appliance_status and appliance_status != "Disposed":
				frappe.msgprint(
					_("Consider setting {0} status to Disposed").format(
						self.linked_appliance
					),
					alert=True,
				)
