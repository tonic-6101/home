# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.model.document import Document
from frappe.utils import today


class HomePhoto(Document):
	def before_save(self):
		if self.property:
			self.household = frappe.db.get_value("Home Property", self.property, "household")
		if not self.photo_date:
			self.photo_date = today()
		if self.purpose != "Renovation":
			self.before_after = ""
			self.pair_ref = ""

	def on_update(self):
		# Auto-set back-link on paired photo
		if self.pair_ref:
			paired = frappe.get_doc("Home Photo", self.pair_ref)
			if not paired.pair_ref:
				paired.db_set("pair_ref", self.name, update_modified=False)

	def on_trash(self):
		# Clear pair_ref on the paired photo
		if self.pair_ref:
			frappe.db.set_value("Home Photo", self.pair_ref, "pair_ref", "", update_modified=False)
