# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(frappe._("Please log in to access Home"), frappe.AuthenticationError)

	csrf_token = frappe.sessions.get_csrf_token()
	context.csrf_token = csrf_token

	user = frappe.session.user
	user_doc = frappe.get_cached_doc("User", user)

	boot = {
		"frappe": {
			"csrf_token": csrf_token,
			"user": user,
			"session": {"user": user},
		},
		"user": {
			"full_name": user_doc.full_name,
			"user_image": user_doc.user_image,
		},
		"installed_apps": frappe.get_installed_apps(),
	}

	# Dock boot data if installed
	if "dock" in boot["installed_apps"]:
		boot["dock"] = {"installed": True}

	context.boot = boot
