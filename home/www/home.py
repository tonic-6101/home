# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(frappe._("Please log in to access Home"), frappe.AuthenticationError)

	csrf_token = frappe.sessions.get_csrf_token()
	context.csrf_token = csrf_token

	context.boot = get_boot()
	context.boot.csrf_token = csrf_token


def _get_dock_boot():
	"""Return dock boot info if dock is installed, else None."""
	if "dock" not in frappe.get_installed_apps():
		return None
	try:
		from dock.boot import get_boot as dock_get_boot
		return dock_get_boot()
	except Exception:
		return {"installed": True}


def get_boot():
	"""Build boot data for Vue SPA including user session info."""
	user = frappe.session.user
	user_doc = frappe.get_cached_doc("User", user)

	return frappe._dict(
		{
			"frappe": {
				"boot": {
					"user": {
						"name": user,
						"email": user_doc.email or "",
						"full_name": user_doc.full_name or user,
						"user_image": user_doc.user_image or "",
					},
					"user_roles": frappe.get_roles(user),
					"dock": _get_dock_boot(),
				},
				"csrf_token": frappe.sessions.get_csrf_token(),
			},
			"installed_apps": frappe.get_installed_apps(),
			"site_name": frappe.local.site,
		}
	)
