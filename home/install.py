# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Post-install hooks for Home."""

import frappe


def after_install() -> None:
	"""Called after `bench --site <site> install-app home`."""
	_create_roles()


def _create_roles() -> None:
	"""Create Home User and Home Manager roles if they don't exist."""
	for role_name in ("Home User", "Home Manager"):
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc(
				{
					"doctype": "Role",
					"role_name": role_name,
					"desk_access": 1,
					"is_custom": 0,
				}
			).insert(ignore_permissions=True)

	frappe.db.commit()
