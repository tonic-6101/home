# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomeMaintenanceTemplate(Document):
	def validate(self):
		self._guard_system_template()

	def before_delete(self):
		self._guard_system_template()

	def _guard_system_template(self):
		"""Block edits and deletes of system templates.

		Exemptions: during app install (frappe.flags.in_install) so that
		fixture data can be created.
		"""
		if self.is_system_template and not frappe.flags.in_install:
			frappe.throw(_("System templates cannot be edited or deleted"))
