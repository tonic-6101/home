# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import uuid

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class HomeProperty(Document):
	def before_save(self):
		self._set_archived_date()
		self._generate_frame_token()
		self._prune_equity_snapshots()

	def _set_archived_date(self):
		"""Set archived_date when property is archived."""
		if self.is_archived and not self.archived_date:
			self.archived_date = today()
		elif not self.is_archived:
			self.archived_date = None

	def _generate_frame_token(self):
		"""Auto-generate Frame guest token on first save when Frame is installed."""
		if not self.frame_token and "frame" in frappe.get_installed_apps():
			self.frame_token = str(uuid.uuid4())

	def _prune_equity_snapshots(self):
		"""Keep max 60 equity snapshots — prune oldest."""
		if len(self.equity_snapshots) > 60:
			self.equity_snapshots = self.equity_snapshots[-60:]
