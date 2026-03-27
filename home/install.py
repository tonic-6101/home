# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Post-install hooks for Home."""

import frappe


def after_install() -> None:
	"""Called after `bench --site <site> install-app home`."""
	_create_roles()
	_create_system_letter_templates()
	_create_seasonal_checklist_templates()
	setup_orga_custom_fields()
	setup_repo_custom_fields()


def setup_orga_custom_fields() -> None:
	"""Add Home context fields to Orga Task as custom fields.

	Called on after_install and after_migrate. Only runs when Orga is installed.
	Uses the same pattern as Orga's setup_watch_custom_fields().
	"""
	if "orga" not in frappe.get_installed_apps():
		return

	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	custom_fields = {
		"Orga Task": [
			{
				"fieldname": "home_section",
				"fieldtype": "Section Break",
				"label": "Home Context",
				"insert_after": "last_frappe_sync",
				"collapsible": 1,
				"depends_on": "eval:doc.home_property",
			},
			{
				"fieldname": "home_property",
				"fieldtype": "Link",
				"label": "Property",
				"options": "Home Property",
				"insert_after": "home_section",
			},
			{
				"fieldname": "home_room",
				"fieldtype": "Link",
				"label": "Room",
				"options": "Home Room",
				"insert_after": "home_property",
				"depends_on": "eval:doc.home_property",
			},
			{
				"fieldname": "home_col_break",
				"fieldtype": "Column Break",
				"insert_after": "home_room",
			},
			{
				"fieldname": "home_item",
				"fieldtype": "Link",
				"label": "Item",
				"options": "Home Item",
				"insert_after": "home_col_break",
				"depends_on": "eval:doc.home_property",
			},
			{
				"fieldname": "home_contractor",
				"fieldtype": "Link",
				"label": "Contractor",
				"options": "Contact",
				"insert_after": "home_item",
			},
			{
				"fieldname": "home_maintenance_category",
				"fieldtype": "Select",
				"label": "Maintenance Category",
				"options": "\nPlumbing\nElectrical\nHVAC & Heating\nPainting & Decorating\nCarpentry\nRoofing & Gutters\nCleaning\nGarden & Landscaping\nPest Control\nInspection\nGeneral Repair\nOther",
				"insert_after": "home_contractor",
			},
			{
				"fieldname": "tender_post",
				"fieldtype": "Data",
				"label": "Tender Post",
				"insert_after": "home_maintenance_category",
				"read_only": 1,
				"hidden": 1,
				"description": "Back-link to Tender Post created from this task",
			},
		],
	}

	create_custom_fields(custom_fields, update=True)


def setup_repo_custom_fields() -> None:
	"""Add Home context fields to Explorer Entry as custom fields.

	Called on after_install and after_migrate. Only runs when Repo is installed.
	Same pattern as setup_orga_custom_fields().
	"""
	if "repo" not in frappe.get_installed_apps():
		return

	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	custom_fields = {
		"Explorer Entry": [
			{
				"fieldname": "home_section",
				"fieldtype": "Section Break",
				"label": "Home Context",
				"insert_after": "pair_ref",
				"collapsible": 1,
				"depends_on": "eval:doc.home_property",
			},
			{
				"fieldname": "home_property",
				"fieldtype": "Link",
				"label": "Property",
				"options": "Home Property",
				"insert_after": "home_section",
			},
			{
				"fieldname": "home_room",
				"fieldtype": "Link",
				"label": "Room",
				"options": "Home Room",
				"insert_after": "home_property",
				"depends_on": "eval:doc.home_property",
			},
			{
				"fieldname": "home_col_break_repo",
				"fieldtype": "Column Break",
				"insert_after": "home_room",
			},
			{
				"fieldname": "home_item",
				"fieldtype": "Link",
				"label": "Item",
				"options": "Home Item",
				"insert_after": "home_col_break_repo",
				"depends_on": "eval:doc.home_property",
			},
			{
				"fieldname": "home_household",
				"fieldtype": "Link",
				"label": "Household",
				"options": "Home Household",
				"insert_after": "home_item",
				"read_only": 1,
				"hidden": 1,
			},
		],
	}

	create_custom_fields(custom_fields, update=True)


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



def _create_system_letter_templates() -> None:
	"""Create the six system letter templates shipped with Home."""

	TEMPLATES = [
		{
			"template_name": "Warranty Claim — Defective Product",
			"situation_type": "Warranty Claim",
			"context_doctype": "Home Warranty",
			"subject_template": "Warranty Claim — {{ item_name }} (S/N {{ serial_number }})",
			"body_template": (
				"{{ sender_name }}<br>{{ property_address }}<br>{{ sender_email }}<br><br>"
				"{{ today }}<br><br>"
				"Dear {{ warranty_provider }} Customer Service,<br><br>"
				"I am writing to make a formal warranty claim regarding my {{ brand }} {{ item_name }}, "
				"purchased on {{ purchase_date }} for {{ purchase_price }}.<br><br>"
				"The appliance is covered by a {{ warranty_type }} warranty valid until {{ warranty_end_date }}.<br><br>"
				"The appliance has developed the following fault:<br><br>"
				"[DESCRIBE THE FAULT IN DETAIL]<br><br>"
				"I request that you arrange for repair or replacement under the terms of the warranty. "
				"Please contact me at the address or email above to arrange an inspection at your earliest convenience.<br><br>"
				"Yours sincerely,<br>{{ sender_name }}"
			),
		},
		{
			"template_name": "Warranty Claim — Rejected (Appeal)",
			"situation_type": "Warranty Claim",
			"context_doctype": "Home Warranty",
			"subject_template": "Appeal: Rejected Warranty Claim — {{ item_name }} (S/N {{ serial_number }})",
			"body_template": (
				"{{ sender_name }}<br>{{ property_address }}<br>{{ sender_email }}<br><br>"
				"{{ today }}<br><br>"
				"Dear {{ warranty_provider }} Customer Service,<br><br>"
				"I am writing to appeal the rejection of my warranty claim regarding my {{ brand }} {{ item_name }} "
				"(Serial Number: {{ serial_number }}), purchased on {{ purchase_date }}.<br><br>"
				"The appliance is covered by a {{ warranty_type }} warranty valid until {{ warranty_end_date }}. "
				"I believe the claim was incorrectly rejected for the following reasons:<br><br>"
				"[EXPLAIN WHY THE REJECTION IS INCORRECT]<br><br>"
				"I request that you reconsider this decision and arrange for repair or replacement under the terms "
				"of the warranty. If this matter is not resolved, I will escalate my complaint to "
				"[CONSUMER PROTECTION BODY / OMBUDSMAN].<br><br>"
				"Yours sincerely,<br>{{ sender_name }}"
			),
		},
		{
			"template_name": "Utility Billing Error",
			"situation_type": "Utility Billing",
			"context_doctype": "Home Utility Bill",
			"subject_template": "Billing Dispute — {{ utility_type }} ({{ period_start }} – {{ period_end }})",
			"body_template": (
				"{{ sender_name }}<br>{{ property_address }}<br>{{ sender_email }}<br><br>"
				"{{ today }}<br><br>"
				"Dear {{ provider }} Customer Service,<br><br>"
				"I am writing to dispute my {{ utility_type }} bill for the period {{ period_start }} to "
				"{{ period_end }}. The amount billed is {{ amount_billed }}.<br><br>"
				"I believe this bill is incorrect for the following reasons:<br><br>"
				"[EXPLAIN WHY THE BILL IS INCORRECT — e.g. METER READINGS, ESTIMATED vs ACTUAL, "
				"UNUSUAL INCREASE]<br><br>"
				"My meter readings for this period were: start {{ reading_start }}, end {{ reading_end }}.<br><br>"
				"I request that you review this bill and issue a corrected invoice. Please respond within "
				"14 days.<br><br>"
				"Yours sincerely,<br>{{ sender_name }}"
			),
		},
		{
			"template_name": "Insurance Claim Notification",
			"situation_type": "Insurance Claim",
			"context_doctype": "Home Insurance Policy",
			"subject_template": "Insurance Claim Notification — Policy {{ policy_number }}",
			"body_template": (
				"{{ sender_name }}<br>{{ property_address }}<br>{{ sender_email }}<br><br>"
				"{{ today }}<br><br>"
				"Dear {{ provider }} Claims Department,<br><br>"
				"I am writing to notify you of a claim under my {{ policy_type }} insurance policy "
				"(policy number: {{ policy_number }}, policy name: {{ policy_name }}).<br><br>"
				"The incident occurred on:<br>"
				"[DATE OF INCIDENT]<br><br>"
				"Description of the incident:<br>"
				"[DESCRIBE WHAT HAPPENED IN DETAIL]<br><br>"
				"Estimated value of the claim: [ESTIMATED AMOUNT]<br>"
				"Policy coverage amount: {{ coverage_amount }}<br><br>"
				"I would appreciate it if you could send me the necessary claim forms and advise on the "
				"next steps. Please contact me at the address or email above.<br><br>"
				"Yours sincerely,<br>{{ sender_name }}"
			),
		},
	]

	frappe.flags.in_install = True
	try:
		for tmpl_data in TEMPLATES:
			if frappe.db.exists(
				"Home Letter Template",
				{"template_name": tmpl_data["template_name"], "is_system_template": 1},
			):
				continue

			doc = frappe.new_doc("Home Letter Template")
			doc.template_name = tmpl_data["template_name"]
			doc.situation_type = tmpl_data["situation_type"]
			doc.context_doctype = tmpl_data["context_doctype"]
			doc.subject_template = tmpl_data["subject_template"]
			doc.body_template = tmpl_data["body_template"]
			doc.is_system_template = 1
			doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.in_install = False

	frappe.db.commit()


def _create_seasonal_checklist_templates() -> None:
	"""Create the four seasonal maintenance checklist templates as Orga Task Templates.

	Only runs when Orga is installed. Creates system templates with tasks
	for Spring, Summer, Autumn, and Winter home maintenance.
	"""
	if "orga" not in frappe.get_installed_apps():
		return

	SEASONAL_TEMPLATES = [
		{
			"template_name": "Spring Home Maintenance",
			"category": "Seasonal",
			"description": "Annual spring maintenance checklist for residential properties.",
			"tasks": [
				{"subject": "Inspect roof for winter damage", "priority": "High", "task_type": "Inspection"},
				{"subject": "Clean gutters and downpipes", "priority": "High", "task_type": "Cleaning"},
				{"subject": "Check exterior walls for cracks", "priority": "Medium", "task_type": "Inspection"},
				{"subject": "Service boiler / heating system", "priority": "Medium", "task_type": "Maintenance"},
				{"subject": "Test smoke and CO detectors", "priority": "High", "task_type": "Safety"},
				{"subject": "Check window seals and caulking", "priority": "Medium", "task_type": "Inspection"},
				{"subject": "Inspect garden drainage", "priority": "Low", "task_type": "Garden"},
				{"subject": "Clean and treat outdoor furniture", "priority": "Low", "task_type": "Cleaning"},
			],
		},
		{
			"template_name": "Summer Home Maintenance",
			"category": "Seasonal",
			"description": "Annual summer maintenance checklist for residential properties.",
			"tasks": [
				{"subject": "Service air conditioning / fans", "priority": "High", "task_type": "Maintenance"},
				{"subject": "Check and repair exterior paint", "priority": "Medium", "task_type": "Painting"},
				{"subject": "Inspect and clean deck or patio", "priority": "Medium", "task_type": "Cleaning"},
				{"subject": "Check plumbing for leaks", "priority": "Medium", "task_type": "Plumbing"},
				{"subject": "Trim trees and hedges near the house", "priority": "Low", "task_type": "Garden"},
				{"subject": "Inspect fence and gate condition", "priority": "Low", "task_type": "Inspection"},
				{"subject": "Clean and organise garage / shed", "priority": "Low", "task_type": "Cleaning"},
			],
		},
		{
			"template_name": "Autumn Home Maintenance",
			"category": "Seasonal",
			"description": "Annual autumn maintenance checklist — prepare for winter.",
			"tasks": [
				{"subject": "Clean gutters and downpipes (pre-winter)", "priority": "High", "task_type": "Cleaning"},
				{"subject": "Test heating system before cold season", "priority": "High", "task_type": "Maintenance"},
				{"subject": "Bleed radiators", "priority": "Medium", "task_type": "Maintenance"},
				{"subject": "Check roof tiles and flashing", "priority": "High", "task_type": "Inspection"},
				{"subject": "Insulate exposed pipes", "priority": "Medium", "task_type": "Maintenance"},
				{"subject": "Check weather stripping on doors", "priority": "Medium", "task_type": "Inspection"},
				{"subject": "Store garden furniture and tools", "priority": "Low", "task_type": "Garden"},
				{"subject": "Test smoke and CO detectors", "priority": "High", "task_type": "Safety"},
			],
		},
		{
			"template_name": "Winter Home Maintenance",
			"category": "Seasonal",
			"description": "Winter maintenance checklist — protect your home during cold months.",
			"tasks": [
				{"subject": "Monitor pipes for freezing risk", "priority": "High", "task_type": "Plumbing"},
				{"subject": "Check attic insulation", "priority": "Medium", "task_type": "Inspection"},
				{"subject": "Clear snow and ice from paths", "priority": "High", "task_type": "Safety"},
				{"subject": "Inspect boiler pressure and function", "priority": "Medium", "task_type": "Maintenance"},
				{"subject": "Check for condensation and mould", "priority": "Medium", "task_type": "Inspection"},
				{"subject": "Verify emergency supplies and contacts", "priority": "Low", "task_type": "Safety"},
			],
		},
	]

	frappe.flags.in_install = True
	try:
		for tmpl_data in SEASONAL_TEMPLATES:
			if frappe.db.exists(
				"Orga Task Template",
				{"template_name": tmpl_data["template_name"], "is_system_template": 1},
			):
				continue

			doc = frappe.new_doc("Orga Task Template")
			doc.template_name = tmpl_data["template_name"]
			doc.category = tmpl_data["category"]
			doc.description = tmpl_data["description"]
			doc.is_system_template = 1

			for task in tmpl_data["tasks"]:
				doc.append("tasks", {
					"subject": task["subject"],
					"priority": task.get("priority", "Medium"),
					"task_type": task.get("task_type", ""),
				})

			doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.in_install = False

	frappe.db.commit()


