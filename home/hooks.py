# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

app_name = "home"
app_title = "Home"
app_publisher = "Tonic"
app_description = (
	"Household management for Frappe"
	" — properties, appliances, maintenance, warranties, inventory, and contractors"
)
app_email = "tonic6101@gmail.com"
app_license = "agpl-3.0"
app_logo_url = "/assets/home/images/home_logo.svg"

# Required apps
# ------------------
# required_apps = []

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
	"color": "#f59e0b",
	"route": "/home",
}

dock_search_sections = [
	{
		"label": "Properties",
		"doctype": "Home Property",
		"search_fields": ["property_name", "city"],
	},
	{
		"label": "Appliances",
		"doctype": "Home Appliance",
		"search_fields": ["appliance_name", "brand", "model"],
	},
	{
		"label": "Contractors",
		"doctype": "Home Contractor",
		"search_fields": ["contractor_name", "trade"],
	},
]

dock_notification_types = [
	{
		"type": "warranty_expiring",
		"label": "Warranty Expiring",
		"icon": "alert-triangle",
	},
	{
		"type": "maintenance_due",
		"label": "Maintenance Due",
		"icon": "tool",
	},
]

# Jana integration (read access + search)
# ------------------
jana_permissions = {
	"Home Property": {"read": True},
	"Home Appliance": {"read": True},
	"Home Maintenance": {"read": True},
	"Home Warranty": {"read": True},
	"Home Inventory Item": {"read": True},
	"Home Contractor": {"read": True},
}

jana_search_providers = [
	{
		"label": "Properties",
		"doctype": "Home Property",
		"search_fields": ["property_name", "city", "address_line1"],
	},
	{
		"label": "Appliances",
		"doctype": "Home Appliance",
		"search_fields": ["appliance_name", "brand", "model", "serial_number"],
	},
	{
		"label": "Maintenance",
		"doctype": "Home Maintenance",
		"search_fields": ["title", "category"],
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
	],
}

# Permissions (household-scoped query conditions)
# ------------------
permission_query_conditions = {
	"Home Property": "home.api.permission.get_household_condition",
	"Home Room": "home.api.permission.get_household_condition",
	"Home Appliance": "home.api.permission.get_household_condition",
	"Home Maintenance": "home.api.permission.get_household_condition",
	"Home Warranty": "home.api.permission.get_household_condition",
	"Home Inventory Item": "home.api.permission.get_household_condition",
	"Home Contractor": "home.api.permission.get_household_condition",
	"Home Purchase Return": "home.api.permission.get_household_condition",
	"Home Settings": "home.api.permission.get_household_condition",
}

has_permission = {
	"Home Property": "home.api.permission.has_household_permission",
	"Home Room": "home.api.permission.has_household_permission",
	"Home Appliance": "home.api.permission.has_household_permission",
	"Home Maintenance": "home.api.permission.has_household_permission",
	"Home Warranty": "home.api.permission.has_household_permission",
	"Home Inventory Item": "home.api.permission.has_household_permission",
	"Home Contractor": "home.api.permission.has_household_permission",
	"Home Purchase Return": "home.api.permission.has_household_permission",
	"Home Settings": "home.api.permission.has_household_permission",
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
