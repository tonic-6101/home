# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomeAppliance(Document):
	def before_insert(self):
		self._populate_expected_lifespan()

	def before_save(self):
		self._fetch_household()

	def on_update(self):
		self._check_disposal()

	def _populate_expected_lifespan(self):
		"""Auto-populate expected_lifespan_years from category defaults if not set."""
		if self.expected_lifespan_years:
			return

		if not self.property:
			return

		household = frappe.db.get_value("Home Property", self.property, "household")
		if not household:
			return

		# Look up the lifespan default from Home Settings
		settings = frappe.db.get_value("Home Settings", {"household": household}, "name")
		if not settings:
			return

		lifespan_rows = frappe.get_all(
			"Home Appliance Category Lifespan",
			filters={"parent": settings, "category": self.category},
			fields=["lifespan_years"],
			limit=1,
		)

		if lifespan_rows:
			self.expected_lifespan_years = lifespan_rows[0].lifespan_years

	def _fetch_household(self):
		"""Fetch household from the linked property for scoping."""
		if self.property:
			household = frappe.db.get_value("Home Property", self.property, "household")
			if household:
				self.household = household

	def _check_disposal(self):
		"""Log a comment when status changes to Disposed."""
		if not self.has_value_changed("status"):
			return

		if self.status == "Disposed":
			self.add_comment(
				"Info",
				_("Appliance marked as Disposed. Consider updating warranty and maintenance records."),
			)
