# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe import _
from frappe.model.document import Document


class HomeHousehold(Document):
	def after_insert(self):
		self._ensure_creator_is_owner()
		self._create_default_settings()

	def validate(self):
		self._validate_at_least_one_owner()
		self._validate_unique_users()

	def on_update(self):
		self._sync_user_permissions()

	def _ensure_creator_is_owner(self):
		"""Auto-insert the creating user as an Owner member if not already present."""
		user = frappe.session.user
		existing_users = [m.user for m in self.members if m.user]

		if user not in existing_users:
			self.append(
				"members",
				{
					"display_name": frappe.db.get_value("User", user, "full_name") or user,
					"role": "Owner",
					"user": user,
				},
			)
			self.save(ignore_permissions=True)

	def _create_default_settings(self):
		"""Auto-create a Home Settings record for this household with defaults."""
		if not frappe.db.exists("Home Settings", {"household": self.name}):
			settings = frappe.new_doc("Home Settings")
			settings.household = self.name
			settings.warranty_alert_days_1 = 90
			settings.warranty_alert_days_2 = 30
			settings.maintenance_reminder_days = 3
			settings.refund_overdue_days = 14
			settings.insurance_renewal_days = 60
			settings.financial_visibility = "Owner and Adult"

			# Populate default lifespan values
			defaults = [
				("White Goods", 12, 600),
				("HVAC", 15, 2500),
				("Heating", 20, 3000),
				("Electronics", 7, 400),
				("Kitchen", 10, 350),
				("Plumbing", 25, 800),
				("Other", 10, 500),
			]
			for category, lifespan, cost in defaults:
				settings.append(
					"lifespan_defaults",
					{
						"category": category,
						"lifespan_years": lifespan,
						"avg_replacement_cost": cost,
					},
				)

			settings.insert(ignore_permissions=True)

	def _validate_at_least_one_owner(self):
		"""Household must always have at least one Owner member."""
		owners = [m for m in self.members if m.role == "Owner"]
		if not owners:
			frappe.throw(_("A household must have at least one Owner member"))

	def _validate_unique_users(self):
		"""Each linked user must appear only once in the members table."""
		users = [m.user for m in self.members if m.user]
		if len(users) != len(set(users)):
			frappe.throw(_("Each user can only appear once in the household"))

	def _sync_user_permissions(self):
		"""Grant/revoke Frappe User Permissions for household members.

		Members with a `user` set get a User Permission for this household.
		Removed members have their User Permission deleted.
		"""
		current_users = {m.user for m in self.members if m.user}

		existing_perms = frappe.get_all(
			"User Permission",
			filters={
				"allow": "Home Household",
				"for_value": self.name,
			},
			pluck="user",
		)
		existing_users = set(existing_perms)

		# Grant new permissions
		for user in current_users - existing_users:
			frappe.get_doc(
				{
					"doctype": "User Permission",
					"user": user,
					"allow": "Home Household",
					"for_value": self.name,
				}
			).insert(ignore_permissions=True)

		# Revoke removed permissions
		for user in existing_users - current_users:
			perms = frappe.get_all(
				"User Permission",
				filters={
					"user": user,
					"allow": "Home Household",
					"for_value": self.name,
				},
				pluck="name",
			)
			for perm in perms:
				frappe.delete_doc("User Permission", perm, ignore_permissions=True)
