# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

app_name = "home"
app_title = "Home"
app_publisher = "Tonic"
app_description = (
	"Household management for Frappe"
	" — properties, items, maintenance, warranties, and more"
)
app_email = "tonic6101@gmail.com"
app_license = "agpl-3.0"
app_logo_url = "/assets/home/images/home_logo.svg"

# SPA route — serve home.html for all /home/* sub-routes
website_route_rules = [
	{"from_route": "/home/<path:app_path>", "to_route": "home"},
]

# Required apps
# ------------------
required_apps = ["frappe", "dock"]

# Apps screen entry (Frappe Desk sidebar)
add_to_apps_screen = [
	{
		"name": "home",
		"logo": "/assets/home/images/home_logo.svg",
		"title": "Home",
		"route": "/home",
		"has_permission": "home.api.permission.has_app_permission",
	}
]

# Dock integration
# ------------------
dock_app_registry = {
	"label": "Home",
	"icon": "home",
	"logo": "/assets/home/images/home_logo.svg",
	"color": "#f59e0b",
	"route": "/home",
	"description": "Property, items, and household management",
}

dock_search_sections = [
	{
		"label": "Properties",
		"doctype": "Home Property",
		"search_fields": ["property_name", "city", "address_line1"],
		"display_field": "property_name",
		"subtitle_field": "city",
		"route": "/home/property/{name}",
	},
	{
		"label": "Items",
		"doctype": "Home Item",
		"search_fields": ["item_name", "brand", "model", "serial_number"],
		"display_field": "item_name",
		"subtitle_field": "brand",
		"route": "/home/property/{property}/items/{name}",
	},
]

dock_notification_types = [
	{
		"type": "warranty_expiring",
		"label": "Warranty Expiring",
		"icon": "alert-triangle",
		"source_app": "home",
		"source_doctype": "Home Warranty",
		"route_template": "/home/property/{property}/warranties/{name}",
	},
	{
		"type": "maintenance_due",
		"label": "Maintenance Due",
		"icon": "tool",
		"source_app": "home",
		"source_doctype": "Home Maintenance",
		"route_template": "/home/property/{property}/maintenance/{name}",
	},
	{
		"type": "insurance_renewal",
		"label": "Insurance Renewal",
		"icon": "shield",
		"source_app": "home",
		"source_doctype": "Home Insurance Policy",
		"route_template": "/home/property/{property}/insurance/{name}",
	},
	{
		"type": "bill_due",
		"label": "Bill Due",
		"icon": "file-text",
		"source_app": "home",
		"source_doctype": "Home Utility Bill",
		"route_template": "/home/property/{property}/utility/{name}",
	},
	{
		"type": "refund_overdue",
		"label": "Refund Overdue",
		"icon": "rotate-ccw",
		"source_app": "home",
		"source_doctype": "Home Purchase Return",
		"route_template": "/home/property/{property}/returns/{name}",
	},
	{
		"type": "recall_alert",
		"label": "Item Recall",
		"icon": "alert-octagon",
		"source_app": "home",
		"source_doctype": "Home Item",
		"route_template": "/home/property/{property}/items/{name}",
	},
	{
		"type": "equity_update",
		"label": "Equity Update Reminder",
		"icon": "trending-up",
		"source_app": "home",
		"source_doctype": "Home Property",
		"route_template": "/home/property/{name}/equity",
	},
]

# Jana integration (endpoint permissions + search)
# ------------------
jana_permissions = [
	{
		"label": "Home — Properties",
		"description": "Property details, rooms, and health scores",
		"endpoints": [
			"home.api.property.get_property",
			"home.api.property.get_health_score",
			"home.api.property.get_repair_fund",
		],
		"scoping": "household",
	},
	{
		"label": "Home — Items",
		"description": "Item list, lifetime costs, and cost comparison",
		"endpoints": [
			"home.api.item.get_lifetime_cost",
			"home.api.item.get_cost_comparison",
		],
		"scoping": "household",
	},
	{
		"label": "Home — Maintenance",
		"description": "Maintenance history and upcoming tasks",
		"endpoints": [
			"home.api.property.get_maintenance_list",
		],
		"scoping": "household",
	},
	{
		"label": "Home — Warranties",
		"description": "Warranty records and expiry status",
		"endpoints": [
			"home.api.warranty.get_warranties",
		],
		"scoping": "household",
	},
	{
		"label": "Home — Financial summary",
		"description": "Annual cost report and budget overview",
		"endpoints": [
			"home.api.report.get_annual_summary",
			"home.api.budget.get_overview",
		],
		"scoping": "household",
		"minimum_role": "Adult",
	},
]

jana_search_providers = [
	{
		"label": "Properties",
		"doctype": "Home Property",
		"search_fields": ["property_name", "city"],
		"summary_endpoint": "home.api.property.get_property",
	},
	{
		"label": "Items",
		"doctype": "Home Item",
		"search_fields": ["item_name", "brand", "model", "serial_number"],
		"summary_endpoint": "home.api.item.get_lifetime_cost",
	},
]

# Frame integration (guest pages)
# ------------------
frame_guest_pages = [
	{
		"route": "/home/guest/property/:token",
		"handler": "home.api.frame.get_property_guest",
		"label": "Property Overview",
	},
]

# Roles
# ------------------
# Home User: standard household member (Adult or Child)
# Home Manager: household Owner — full control including settings and member management

# Scheduled Tasks
# ------------------
scheduler_events = {
	"daily": [
		"home.tasks.send_warranty_expiry_alerts",
		"home.tasks.send_maintenance_reminders",
		"home.tasks.send_insurance_renewal_alerts",
		"home.tasks.send_unpaid_bill_reminders",
		"home.tasks.send_overdue_refund_alerts",
		"home.tasks.send_equity_update_reminders",
	],
	"weekly": [
		"home.tasks.check_item_recalls",
	],
}

# Permissions (household-scoped query conditions)
# ------------------
permission_query_conditions = {
	"Home Property": "home.api.permission.get_household_condition",
	"Home Room": "home.api.permission.get_household_condition",
	"Home Item": "home.api.permission.get_household_condition",
	"Home Maintenance": "home.api.permission.get_household_condition",
	"Home Warranty": "home.api.permission.get_household_condition",
	"Home Purchase Return": "home.api.permission.get_household_condition",
	"Home Settings": "home.api.permission.get_household_condition",
	"Home Utility Bill": "home.api.permission.get_household_condition",
	"Home Insurance Policy": "home.api.permission.get_household_condition",
	"Home Budget": "home.api.permission.get_household_condition",
	"Home Mortgage": "home.api.permission.get_household_condition",
	"Home Generated Letter": "home.api.permission.get_household_condition",
	"Home Improvement Wish": "home.api.permission.get_household_condition",
	"Home Photo": "home.api.permission.get_household_condition",
}

has_permission = {
	"Home Property": "home.api.permission.has_household_permission",
	"Home Room": "home.api.permission.has_household_permission",
	"Home Item": "home.api.permission.has_household_permission",
	"Home Maintenance": "home.api.permission.has_household_permission",
	"Home Warranty": "home.api.permission.has_household_permission",
	"Home Purchase Return": "home.api.permission.has_household_permission",
	"Home Settings": "home.api.permission.has_household_permission",
	"Home Utility Bill": "home.api.permission.has_household_permission",
	"Home Insurance Policy": "home.api.permission.has_household_permission",
	"Home Budget": "home.api.permission.has_household_permission",
	"Home Mortgage": "home.api.permission.has_household_permission",
	"Home Generated Letter": "home.api.permission.has_household_permission",
	"Home Improvement Wish": "home.api.permission.has_household_permission",
	"Home Photo": "home.api.permission.has_household_permission",
}

# Doc Events
# ------------------
doc_events = {
	"User": {
		"after_insert": "home.api.household.link_user_to_pending_invitations",
	},
}

# Installation
# ------------------
after_install = "home.install.after_install"

# Fixtures
# ------------------
fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Home User", "Home Manager"]]],
	},
]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True
