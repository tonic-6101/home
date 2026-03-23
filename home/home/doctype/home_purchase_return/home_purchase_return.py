# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomePurchaseReturn(Document):
	def before_insert(self):
		if self.property:
			from home.api.permission import require_property_not_archived

			require_property_not_archived(self.property)

	def before_save(self):
		self._fetch_household()

	def on_update(self):
		self._auto_set_refund_date()
		self._suggest_item_disposal()

	def _auto_set_refund_date(self):
		"""Auto-set refund_received_date to today when status → Received and date is empty."""
		if (
			self.has_value_changed("refund_status")
			and self.refund_status in ("Received", "Partially Received")
			and not self.refund_received_date
		):
			from frappe.utils import today

			self.refund_received_date = today()
			self.db_set("refund_received_date", self.refund_received_date)

	def _fetch_household(self):
		"""Auto-fetch household from the linked property."""
		if self.property:
			self.household = frappe.db.get_value(
				"Home Property", self.property, "household"
			)

	def _suggest_item_disposal(self):
		"""If linked item is an appliance and reason is Defective, suggest marking it Disposed."""
		if (
			self.linked_item
			and self.return_reason == "Defective"
			and self.has_value_changed("return_reason")
		):
			item_data = frappe.db.get_value(
				"Home Item", self.linked_item, ["status", "item_type"], as_dict=True
			)
			if item_data and item_data.item_type == "Appliance" and item_data.status != "Disposed":
				frappe.msgprint(
					_("Consider setting {0} status to Disposed").format(
						self.linked_item
					),
					alert=True,
				)
