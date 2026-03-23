# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.model.document import Document
from frappe.utils import today


class HomeMortgage(Document):
	def before_insert(self):
		if self.property:
			from home.api.permission import require_property_not_archived

			require_property_not_archived(self.property)

	def before_save(self):
		if self.property:
			self.household = frappe.db.get_value("Home Property", self.property, "household")

	def on_update(self):
		if self.has_value_changed("outstanding_balance"):
			self._trigger_equity_snapshot()

	def _trigger_equity_snapshot(self):
		"""Append an equity snapshot to the linked property when balance changes."""
		prop = frappe.get_doc("Home Property", self.property)

		mortgages = frappe.get_all(
			"Home Mortgage",
			filters={"property": self.property},
			fields=["outstanding_balance"],
		)
		total_balance = sum((m.get("outstanding_balance") or 0) for m in mortgages)
		value = prop.estimated_value or 0
		equity = value - total_balance
		pct = (equity / value * 100) if value else 0

		prop.append("equity_snapshots", {
			"snapshot_date": today(),
			"estimated_value": value,
			"total_mortgage_balance": total_balance,
			"equity_amount": equity,
			"equity_pct": round(pct, 1),
			"note": "Mortgage balance updated",
		})

		# Prune to 60 most recent
		if len(prop.equity_snapshots) > 60:
			prop.equity_snapshots = sorted(
				prop.equity_snapshots, key=lambda s: s.snapshot_date
			)[-60:]

		prop.save(ignore_permissions=True)
