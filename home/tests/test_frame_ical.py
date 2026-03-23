# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for Frame guest portal and iCal subscription feed."""

import uuid

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days

from home.api.frame import get_property_guest
from home.api.ical import get_property_feed, _escape_ical
from home.home.doctype.home_property.home_property import (
	regenerate_frame_token,
	regenerate_ical_token,
)


class TestFrameGuest(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Frame Guest Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Frame Guest Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_frame_guest_api(self):
		"""Frame guest API should return property data via token."""
		_hh, prop = self._setup()

		prop.frame_token = str(uuid.uuid4())
		prop.save(ignore_permissions=True)

		result = get_property_guest(prop.frame_token)
		self.assertEqual(result["property"]["property_name"], "Frame Guest Test House")


class TestIcalFeed(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "iCal Feed Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "The Cottage",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def _get_feed_content(self, token: str) -> str:
		"""Call get_property_feed and extract the iCal content from the response."""
		get_property_feed(token)
		return frappe.local.response["filecontent"].decode("utf-8")

	def test_ical_token_auto_generated(self):
		_hh, prop = self._setup()
		self.assertTrue(prop.ical_token)
		# Should be a valid UUID
		uuid.UUID(prop.ical_token)

	def test_feed_returns_vcalendar(self):
		_hh, prop = self._setup()
		content = self._get_feed_content(prop.ical_token)

		self.assertTrue(content.startswith("BEGIN:VCALENDAR"))
		self.assertIn("END:VCALENDAR", content)
		self.assertIn("VERSION:2.0", content)
		self.assertIn("PRODID:", content)
		self.assertIn("METHOD:PUBLISH", content)

	def test_feed_calendar_name(self):
		_hh, prop = self._setup()
		content = self._get_feed_content(prop.ical_token)

		self.assertIn("X-WR-CALNAME:The Cottage — Maintenance", content)

	def test_feed_contains_scheduled_tasks(self):
		_hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Annual boiler service",
				"property": prop.name,
				"maintenance_type": "One-off",
				"category": "HVAC & Heating",
				"status": "Scheduled",
				"scheduled_date": "2026-04-15",
			}
		).insert(ignore_permissions=True)

		content = self._get_feed_content(prop.ical_token)

		self.assertIn("BEGIN:VEVENT", content)
		self.assertIn("Annual boiler service", content)
		self.assertIn("The Cottage", content)
		self.assertIn("DTSTART;VALUE=DATE:20260415", content)
		self.assertIn("DTEND;VALUE=DATE:20260416", content)
		self.assertIn("STATUS:CONFIRMED", content)
		self.assertIn("Category: HVAC & Heating", content)

	def test_feed_contains_in_progress_tasks(self):
		_hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Roof repair",
				"property": prop.name,
				"maintenance_type": "One-off",
				"category": "Roofing & Gutters",
				"status": "In Progress",
				"scheduled_date": "2026-03-10",
			}
		).insert(ignore_permissions=True)

		content = self._get_feed_content(prop.ical_token)

		self.assertIn("Roof repair", content)
		self.assertIn("STATUS:IN-PROCESS", content)

	def test_feed_excludes_completed_and_cancelled(self):
		_hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Completed task",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Completed",
				"scheduled_date": "2026-01-10",
				"completed_date": "2026-01-10",
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Cancelled task",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Cancelled",
				"scheduled_date": "2026-02-01",
			}
		).insert(ignore_permissions=True)

		content = self._get_feed_content(prop.ical_token)

		self.assertNotIn("Completed task", content)
		self.assertNotIn("Cancelled task", content)

	def test_feed_excludes_tasks_without_date(self):
		_hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Undated task",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Scheduled",
			}
		).insert(ignore_permissions=True)

		content = self._get_feed_content(prop.ical_token)

		self.assertNotIn("Undated task", content)

	def test_uid_includes_site_name(self):
		_hh, prop = self._setup()

		task = frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "UID test task",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Scheduled",
				"scheduled_date": today(),
			}
		).insert(ignore_permissions=True)

		content = self._get_feed_content(prop.ical_token)

		site = frappe.local.site
		self.assertIn(f"UID:{task.name}@{site}", content)

	def test_uid_stable_across_refreshes(self):
		"""UID should not change between feed requests."""
		_hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Stable UID task",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Scheduled",
				"scheduled_date": today(),
			}
		).insert(ignore_permissions=True)

		content1 = self._get_feed_content(prop.ical_token)
		content2 = self._get_feed_content(prop.ical_token)

		# Extract UIDs
		uid1 = [l for l in content1.split("\r\n") if l.startswith("UID:")]
		uid2 = [l for l in content2.split("\r\n") if l.startswith("UID:")]
		self.assertEqual(uid1, uid2)

	def test_contractor_in_description(self):
		_hh, prop = self._setup()

		contractor = frappe.get_doc(
			{
				"doctype": "Contact",
				"first_name": "Mike's Plumbing",
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Fix tap",
				"property": prop.name,
				"maintenance_type": "One-off",
				"category": "Plumbing",
				"status": "Scheduled",
				"scheduled_date": today(),
				"contractor": contractor.name,
			}
		).insert(ignore_permissions=True)

		content = self._get_feed_content(prop.ical_token)

		self.assertIn("Contractor: Mike's Plumbing", content)

	def test_invalid_token_rejected(self):
		with self.assertRaises(frappe.PermissionError):
			get_property_feed("not-a-real-token")

	def test_empty_token_rejected(self):
		with self.assertRaises(frappe.AuthenticationError):
			get_property_feed("")

	def test_archived_property_feed_rejected(self):
		_hh, prop = self._setup()
		token = prop.ical_token

		prop.is_archived = 1
		prop.save(ignore_permissions=True)

		with self.assertRaises(frappe.PermissionError):
			get_property_feed(token)

	def test_response_metadata(self):
		_hh, prop = self._setup()
		get_property_feed(prop.ical_token)

		self.assertEqual(frappe.local.response["type"], "download")
		self.assertIn(".ics", frappe.local.response["filename"])
		self.assertEqual(
			frappe.local.response["content_type"],
			"text/calendar; charset=utf-8",
		)

	def test_filename_uses_property_slug(self):
		_hh, prop = self._setup()
		get_property_feed(prop.ical_token)

		self.assertEqual(
			frappe.local.response["filename"],
			"home-the_cottage.ics",
		)

	def test_feed_url_contains_task_link(self):
		_hh, prop = self._setup()

		task = frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "URL test",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Scheduled",
				"scheduled_date": today(),
			}
		).insert(ignore_permissions=True)

		content = self._get_feed_content(prop.ical_token)

		self.assertIn(f"URL:https://{frappe.local.site}/home/maintenance/{task.name}", content)


class TestIcalTokenRegeneration(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "iCal Regen Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Regen Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_regenerate_produces_new_token(self):
		_hh, prop = self._setup()
		old_token = prop.ical_token

		new_token = regenerate_ical_token(prop.name)

		self.assertNotEqual(old_token, new_token)
		uuid.UUID(new_token)  # valid UUID

	def test_old_token_invalid_after_regeneration(self):
		_hh, prop = self._setup()
		old_token = prop.ical_token

		regenerate_ical_token(prop.name)

		with self.assertRaises(frappe.PermissionError):
			get_property_feed(old_token)

	def test_regenerate_owner_only(self):
		hh, prop = self._setup()

		if not frappe.db.exists("User", "icaladult@example.com"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "icaladult@example.com",
					"first_name": "IcalAdult",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		hh.append(
			"members",
			{"display_name": "Adult", "role": "Adult", "user": "icaladult@example.com"},
		)
		hh.save(ignore_permissions=True)

		frappe.set_user("icaladult@example.com")
		try:
			self.assertRaises(
				frappe.PermissionError,
				regenerate_ical_token,
				property=prop.name,
			)
		finally:
			frappe.set_user("Administrator")


class TestIcalEscape(FrappeTestCase):
	def test_escapes_special_chars(self):
		self.assertEqual(_escape_ical("hello, world"), "hello\\, world")
		self.assertEqual(_escape_ical("a;b"), "a\\;b")
		self.assertEqual(_escape_ical("line1\nline2"), "line1\\nline2")
		self.assertEqual(_escape_ical("back\\slash"), "back\\\\slash")

	def test_empty_string(self):
		self.assertEqual(_escape_ical(""), "")
		self.assertEqual(_escape_ical(None), "")
