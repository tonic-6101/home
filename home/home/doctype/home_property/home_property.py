# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import uuid

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class HomeProperty(Document):
	def before_insert(self):
		self._enforce_single_property()
		self._set_country_default()

	def validate(self):
		self._require_owner_for_edit()

	def _enforce_single_property(self):
		"""Community tier: one active (non-archived) property per household.

		Pro tier (home_pro installed) lifts this restriction.
		"""
		if "home_pro" in frappe.get_installed_apps():
			return

		if not self.household:
			return

		existing = frappe.db.count(
			"Home Property",
			{"household": self.household, "is_archived": 0},
		)
		if existing >= 1:
			frappe.throw(
				_("Your household already has a property. "
				  "Archive the existing property before creating a new one, "
				  "or edit the existing property instead."),
				frappe.ValidationError,
			)

	def before_save(self):
		self._set_archived_date()
		self._generate_tokens()
		self._prune_equity_snapshots()

	def _require_owner_for_edit(self):
		"""Only Owner household members can edit property details.

		Skipped on insert (create_property API handles access)
		and for ignore_permissions saves (system-triggered, e.g. equity snapshots).
		"""
		if self.is_new() or self.flags.ignore_permissions:
			return

		user = frappe.session.user
		if user == "Administrator":
			return

		from home.api.permission import get_household_role

		role = get_household_role(self.household, user)
		if role != "Owner":
			frappe.throw(
				_("Only the household Owner can edit property details"),
				frappe.PermissionError,
			)

	def _set_country_default(self):
		"""Default country to the site's default country on creation."""
		if not self.country:
			self.country = frappe.db.get_default("country")

	def _set_archived_date(self):
		"""Set archived_date when property is archived."""
		if self.is_archived and not self.archived_date:
			self.archived_date = today()
		elif not self.is_archived:
			self.archived_date = None

	def _generate_tokens(self):
		"""Auto-generate Frame and iCal tokens on first save when apps are installed."""
		if not self.frame_token and "frame" in frappe.get_installed_apps():
			self.frame_token = str(uuid.uuid4())
		if not self.ical_token:
			self.ical_token = str(uuid.uuid4())

	def _prune_equity_snapshots(self):
		"""Keep max 60 equity snapshots — prune oldest."""
		if len(self.equity_snapshots) > 60:
			self.equity_snapshots = self.equity_snapshots[-60:]


@frappe.whitelist()
def regenerate_frame_token(property: str) -> str:
	"""Regenerate Frame guest token for a property. Owner only."""
	from home.api.permission import require_household_access, require_role

	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Owner")

	prop.frame_token = str(uuid.uuid4())
	prop.save(ignore_permissions=True)
	return prop.frame_token


@frappe.whitelist()
def regenerate_ical_token(property: str) -> str:
	"""Regenerate iCal subscription token for a property. Owner only."""
	from home.api.permission import require_household_access, require_role

	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Owner")

	prop.ical_token = str(uuid.uuid4())
	prop.save(ignore_permissions=True)
	return prop.ical_token
