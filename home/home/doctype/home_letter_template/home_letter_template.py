# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomeLetterTemplate(Document):
	def validate(self):
		if self.is_system_template and not self.is_new():
			# Block edits to system templates (except notes)
			changed = self.get_doc_before_save()
			if changed:
				protected = [
					"template_name", "situation_type", "context_doctype",
					"subject_template", "body_template",
				]
				for field in protected:
					if self.get(field) != changed.get(field):
						frappe.throw(
							_("System templates cannot be edited. Duplicate to create a custom version.")
						)

	def on_trash(self):
		if self.is_system_template:
			frappe.throw(_("System templates cannot be deleted"))
