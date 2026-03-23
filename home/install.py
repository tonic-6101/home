# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Post-install hooks for Home."""

import frappe


def after_install() -> None:
	"""Called after `bench --site <site> install-app home`."""
	_create_roles()
	_create_system_maintenance_templates()
	_create_system_letter_templates()
	_create_demo_maintenance_records()


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


def _create_system_maintenance_templates() -> None:
	"""Create the four system maintenance templates shipped with Home."""

	TEMPLATES = [
		{
			"template_name": "Winter Preparation",
			"season": "Winter",
			"description": "Prepare your home for the cold months — heating, pipes, and draft-proofing.",
			"tasks": [
				{"title": "Bleed radiators", "category": "HVAC & Heating", "days_offset": 0},
				{"title": "Check boiler pressure", "category": "HVAC & Heating", "days_offset": 0},
				{"title": "Insulate exposed pipes", "category": "Plumbing", "days_offset": 0},
				{"title": "Clean gutters of autumn leaves", "category": "Roofing & Gutters", "days_offset": 0},
				{"title": "Check smoke and CO detectors", "category": "Inspection", "days_offset": 7},
				{"title": "Seal drafts around windows and doors", "category": "General Repair", "days_offset": 7},
				{"title": "Service heating oil / log delivery", "category": "HVAC & Heating", "days_offset": 14},
			],
		},
		{
			"template_name": "Spring Check",
			"season": "Spring",
			"description": "Inspect your home after winter — roof, exterior, and garden.",
			"tasks": [
				{"title": "Inspect roof for winter damage", "category": "Roofing & Gutters", "days_offset": 0},
				{"title": "Clean gutters", "category": "Roofing & Gutters", "days_offset": 0},
				{"title": "Check exterior paint and woodwork", "category": "Painting & Decorating", "days_offset": 0},
				{"title": "Service HVAC / AC unit", "category": "HVAC & Heating", "days_offset": 0},
				{"title": "Check garden irrigation", "category": "Garden & Landscaping", "days_offset": 7},
				{"title": "Test outdoor taps and hose bibs", "category": "Plumbing", "days_offset": 7},
			],
		},
		{
			"template_name": "Annual Safety Check",
			"season": "Annual",
			"description": "Yearly safety inspection — boiler, detectors, fire equipment, and electrics.",
			"tasks": [
				{"title": "Annual boiler service", "category": "HVAC & Heating", "days_offset": 0},
				{"title": "Test smoke detectors (replace batteries)", "category": "Inspection", "days_offset": 0},
				{"title": "Test CO detectors", "category": "Inspection", "days_offset": 0},
				{"title": "Check fire extinguisher", "category": "Inspection", "days_offset": 0},
				{"title": "Inspect electrical panel", "category": "Electrical", "days_offset": 0},
				{"title": "Check emergency shutoff locations", "category": "Inspection", "days_offset": 0},
			],
		},
		{
			"template_name": "Move-in Checklist",
			"season": "Move-in",
			"description": "Essential checks when moving into a new property.",
			"tasks": [
				{"title": "Change all door locks", "category": "General Repair", "days_offset": 0},
				{"title": "Test all light switches and sockets", "category": "Electrical", "days_offset": 0},
				{"title": "Test all taps and check for leaks", "category": "Plumbing", "days_offset": 0},
				{"title": "Check boiler pressure and pilot", "category": "HVAC & Heating", "days_offset": 0},
				{"title": "Test smoke and CO detectors", "category": "Inspection", "days_offset": 0},
				{"title": "Locate and label all shutoffs", "category": "Inspection", "days_offset": 0},
				{"title": "Deep clean all rooms", "category": "Cleaning", "days_offset": 0},
				{"title": "Inspect windows and seals", "category": "General Repair", "days_offset": 7},
				{"title": "Check roof and gutters", "category": "Roofing & Gutters", "days_offset": 7},
			],
		},
	]

	frappe.flags.in_install = True
	try:
		for tmpl_data in TEMPLATES:
			if frappe.db.exists(
				"Home Maintenance Template",
				{"template_name": tmpl_data["template_name"], "is_system_template": 1},
			):
				continue

			doc = frappe.new_doc("Home Maintenance Template")
			doc.template_name = tmpl_data["template_name"]
			doc.season = tmpl_data["season"]
			doc.description = tmpl_data["description"]
			doc.is_system_template = 1

			for task in tmpl_data["tasks"]:
				doc.append(
					"tasks",
					{
						"title": task["title"],
						"category": task["category"],
						"days_offset": task["days_offset"],
					},
				)

			doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.in_install = False

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


def _create_demo_maintenance_records() -> None:
	"""Create 10 example maintenance records for demonstration purposes.

	Requires at least one Home Property to exist. Skips silently if none found.
	"""
	prop = frappe.db.get_value("Home Property", {}, "name")
	if not prop:
		return

	# Skip if demo records already exist
	if frappe.db.exists("Home Maintenance", {"title": "Annual boiler service", "property": prop}):
		return

	from frappe.utils import add_days, today

	base_date = today()

	RECORDS = [
		{
			"title": "Annual boiler service",
			"category": "HVAC & Heating",
			"maintenance_type": "Recurring",
			"recurrence": "Annual",
			"status": "Completed",
			"scheduled_date": add_days(base_date, -30),
			"completed_date": add_days(base_date, -28),
			"cost": 180.00,
			"notes": "Engineer checked pressure, flue, and safety valve. All OK.",
		},
		{
			"title": "Fix leaking kitchen tap",
			"category": "Plumbing",
			"maintenance_type": "One-off",
			"status": "Completed",
			"scheduled_date": add_days(base_date, -14),
			"completed_date": add_days(base_date, -12),
			"cost": 95.00,
			"notes": "Replaced ceramic cartridge in mixer tap.",
		},
		{
			"title": "Clean gutters — front and rear",
			"category": "Roofing & Gutters",
			"maintenance_type": "Recurring",
			"recurrence": "Bi-annual",
			"status": "Scheduled",
			"scheduled_date": add_days(base_date, 10),
		},
		{
			"title": "Test smoke and CO detectors",
			"category": "Inspection",
			"maintenance_type": "Recurring",
			"recurrence": "Monthly",
			"status": "Scheduled",
			"scheduled_date": add_days(base_date, 3),
		},
		{
			"title": "Repaint hallway walls",
			"category": "Painting & Decorating",
			"maintenance_type": "One-off",
			"status": "In Progress",
			"scheduled_date": add_days(base_date, -5),
			"cost": 320.00,
			"notes": "Primer done, first coat applied. Finishing coat tomorrow.",
		},
		{
			"title": "Bleed all radiators",
			"category": "HVAC & Heating",
			"maintenance_type": "Recurring",
			"recurrence": "Annual",
			"status": "Completed",
			"scheduled_date": add_days(base_date, -60),
			"completed_date": add_days(base_date, -60),
		},
		{
			"title": "Replace bathroom extractor fan",
			"category": "Electrical",
			"maintenance_type": "One-off",
			"status": "Scheduled",
			"scheduled_date": add_days(base_date, 21),
			"cost": 150.00,
			"notes": "Ordered Xpelair DX100T — arrives next week.",
		},
		{
			"title": "Trim hedges and mow lawn",
			"category": "Garden & Landscaping",
			"maintenance_type": "Recurring",
			"recurrence": "Monthly",
			"status": "Scheduled",
			"scheduled_date": add_days(base_date, 7),
		},
		{
			"title": "Inspect roof tiles after storm",
			"category": "Roofing & Gutters",
			"maintenance_type": "One-off",
			"status": "Completed",
			"scheduled_date": add_days(base_date, -45),
			"completed_date": add_days(base_date, -44),
			"notes": "Found 3 displaced tiles on south side. Repositioned and sealed.",
		},
		{
			"title": "Pest control — annual ant treatment",
			"category": "Pest Control",
			"maintenance_type": "Recurring",
			"recurrence": "Annual",
			"status": "Scheduled",
			"scheduled_date": add_days(base_date, 30),
			"cost": 75.00,
		},
	]

	frappe.flags.in_install = True
	try:
		for rec in RECORDS:
			doc = frappe.new_doc("Home Maintenance")
			doc.property = prop
			doc.title = rec["title"]
			doc.category = rec.get("category")
			doc.maintenance_type = rec["maintenance_type"]
			doc.recurrence = rec.get("recurrence")
			doc.status = rec["status"]
			doc.scheduled_date = rec.get("scheduled_date")
			doc.completed_date = rec.get("completed_date")
			doc.cost = rec.get("cost")
			doc.notes = rec.get("notes")
			doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.in_install = False

	frappe.db.commit()
