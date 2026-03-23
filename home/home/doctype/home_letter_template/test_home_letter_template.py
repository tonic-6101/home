# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHomeLetterTemplate(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Letter Template Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Letter Template Test House",
				"property_type": "Apartment",
				"ownership_status": "Rented",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def _make_system_template(self):
		frappe.flags.in_install = True
		try:
			return frappe.get_doc(
				{
					"doctype": "Home Letter Template",
					"template_name": "System Test Template",
					"situation_type": "Custom",
					"subject_template": "Test subject {{ today }}",
					"body_template": "Dear {{ sender_name }},<br>Test body.",
					"is_system_template": 1,
				}
			).insert(ignore_permissions=True)
		finally:
			frappe.flags.in_install = False

	def test_system_template_not_deletable(self):
		_hh, _prop = self._setup()
		template = self._make_system_template()

		with self.assertRaises(frappe.ValidationError):
			template.delete(ignore_permissions=True)

	def test_system_template_blocks_field_edit(self):
		_hh, _prop = self._setup()
		template = self._make_system_template()

		template.template_name = "Modified Name"
		with self.assertRaises(frappe.ValidationError):
			template.save()

	def test_system_template_allows_notes_edit(self):
		_hh, _prop = self._setup()
		template = self._make_system_template()

		template.notes = "Some user notes"
		template.save()
		self.assertEqual(template.notes, "Some user notes")

	def test_custom_template_editable(self):
		_hh, _prop = self._setup()
		template = frappe.get_doc(
			{
				"doctype": "Home Letter Template",
				"template_name": "Custom Template",
				"situation_type": "Custom",
				"subject_template": "Custom subject",
				"body_template": "Custom body",
				"is_system_template": 0,
			}
		).insert(ignore_permissions=True)

		template.template_name = "Renamed Custom"
		template.save()
		self.assertEqual(template.template_name, "Renamed Custom")

	def test_custom_template_deletable(self):
		_hh, _prop = self._setup()
		template = frappe.get_doc(
			{
				"doctype": "Home Letter Template",
				"template_name": "Deletable Template",
				"situation_type": "Custom",
				"subject_template": "Subject",
				"body_template": "Body",
				"is_system_template": 0,
			}
		).insert(ignore_permissions=True)

		name = template.name
		template.delete()
		self.assertFalse(frappe.db.exists("Home Letter Template", name))


class TestCorrespondenceAPI(FrappeTestCase):
	"""Tests for Feature 35 — Correspondence API."""

	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Correspondence API HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Correspondence Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
				"address_line1": "Musterstraße 12",
				"city": "Munich",
				"postal_code": "80331",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def _make_template(self):
		return frappe.get_doc(
			{
				"doctype": "Home Letter Template",
				"template_name": "Test Warranty Letter",
				"situation_type": "Warranty Claim",
				"context_doctype": "Home Warranty",
				"subject_template": "Warranty Claim — {{ item_name }}",
				"body_template": (
					"Dear {{ warranty_provider }},<br>"
					"My {{ brand }} {{ item_name }} ({{ serial_number }}) needs repair.<br>"
					"Purchased: {{ purchase_date }} for {{ purchase_price }}.<br>"
					"Warranty valid until {{ warranty_end_date }}.<br>"
					"Sincerely, {{ sender_name }}"
				),
			}
		).insert(ignore_permissions=True)

	def test_get_templates(self):
		from home.api.correspondence import get_templates

		_hh, _prop = self._setup()
		self._make_template()

		result = get_templates()
		self.assertIn("templates", result)
		names = [t["template_name"] for t in result["templates"]]
		self.assertIn("Test Warranty Letter", names)

	def test_render_draft_with_warranty_context(self):
		from home.api.correspondence import render_draft

		_hh, prop = self._setup()
		template = self._make_template()

		appliance = frappe.get_doc(
			{
				"doctype": "Home Item",
				"item_type": "Appliance",
				"property": prop.name,
				"item_name": "Bosch Dishwasher",
				"brand": "Bosch",
				"model": "SMV4",
				"serial_number": "9A2B3C4D",
				"purchase_date": "2021-03-15",
				"purchase_price": 480,
			}
		).insert(ignore_permissions=True)

		warranty = frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"item": appliance.name,
				"warranty_type": "Extended",
				"provider": "Bosch",
				"start_date": "2021-03-15",
				"end_date": "2026-03-15",
			}
		).insert(ignore_permissions=True)

		result = render_draft(
			template=template.name,
			context_doctype="Home Warranty",
			context_name=warranty.name,
			property=prop.name,
		)

		self.assertIn("Bosch Dishwasher", result["subject"])
		self.assertIn("9A2B3C4D", result["subject"])
		self.assertIn("Bosch", result["body"])
		self.assertIn("Extended", result["body"])
		self.assertNotIn("{{ ", result["body"])

	def test_render_draft_unfilled_placeholders(self):
		from home.api.correspondence import render_draft

		_hh, prop = self._setup()

		template = frappe.get_doc(
			{
				"doctype": "Home Letter Template",
				"template_name": "Placeholder Test",
				"situation_type": "Custom",
				"subject_template": "Letter about {{ nonexistent_field }}",
				"body_template": "Dear {{ unknown_person }}, test.",
			}
		).insert(ignore_permissions=True)

		result = render_draft(
			template=template.name,
			property=prop.name,
		)

		# Unfilled placeholders should render as [PLACEHOLDER NAME]
		self.assertIn("[NONEXISTENT FIELD]", result["subject"])
		self.assertIn("[UNKNOWN PERSON]", result["body"])

	def test_render_draft_blocked_for_child(self):
		from home.api.correspondence import render_draft

		hh, prop = self._setup()
		template = self._make_template()

		if not frappe.db.exists("User", "letterchild@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "letterchild@example.com",
					"first_name": "LetterChild",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh.append(
			"members",
			{"display_name": "Child", "role": "Child", "user": "letterchild@example.com"},
		)
		hh.save(ignore_permissions=True)

		frappe.set_user("letterchild@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				render_draft,
				template=template.name,
				property=prop.name,
			)
		finally:
			frappe.set_user("Administrator")

	def test_generated_letter_saves_with_household(self):
		hh, prop = self._setup()

		letter = frappe.get_doc(
			{
				"doctype": "Home Generated Letter",
				"property": prop.name,
				"situation_type": "Custom",
				"subject": "Test letter subject",
				"body": "Test letter body",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(letter.household, hh.name)
		self.assertEqual(letter.status, "Draft")
