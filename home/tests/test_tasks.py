# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for scheduled tasks: warranty expiry alerts and maintenance reminders."""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from home.tasks import send_maintenance_reminders, send_warranty_expiry_alerts


class TestWarrantyExpiryAlerts(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Alert Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Alert Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		appliance = frappe.get_doc(
			{
				"doctype": "Home Appliance",
				"appliance_name": "Alert Test Appliance",
				"property": prop.name,
				"category": "White Goods",
				"status": "Working",
			}
		).insert(ignore_permissions=True)

		return hh, prop, appliance

	@patch("home.tasks._send_notification")
	def test_warranty_expiry_alert_fires(self, mock_notify):
		hh, prop, appliance = self._setup()

		# Create a warranty expiring in exactly 90 days
		frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"appliance": appliance.name,
				"warranty_type": "Manufacturer",
				"start_date": "2020-01-01",
				"end_date": add_days(today(), 90),
			}
		).insert(ignore_permissions=True)

		send_warranty_expiry_alerts()
		mock_notify.assert_called()

	@patch("home.tasks._send_notification")
	def test_no_alert_for_far_future_warranty(self, mock_notify):
		hh, prop, appliance = self._setup()

		# Create a warranty expiring in 365 days — should not trigger
		frappe.get_doc(
			{
				"doctype": "Home Warranty",
				"appliance": appliance.name,
				"warranty_type": "Manufacturer",
				"start_date": "2020-01-01",
				"end_date": add_days(today(), 365),
			}
		).insert(ignore_permissions=True)

		send_warranty_expiry_alerts()
		mock_notify.assert_not_called()


class TestMaintenanceReminders(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Reminder Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Reminder Test House",
				"property_type": "Apartment",
				"ownership_status": "Rented",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	@patch("home.tasks._send_notification")
	def test_maintenance_reminder_fires(self, mock_notify):
		hh, prop = self._setup()

		# Task scheduled exactly 3 days from now (default reminder threshold)
		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Reminder Test Task",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Scheduled",
				"scheduled_date": add_days(today(), 3),
			}
		).insert(ignore_permissions=True)

		send_maintenance_reminders()
		mock_notify.assert_called()

	@patch("home.tasks._send_notification")
	def test_no_reminder_for_completed_task(self, mock_notify):
		"""A completed task should not trigger a reminder.

		Uses a dedicated household/property to avoid cross-test pollution.
		"""
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "No Reminder Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "No Reminder Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Home Maintenance",
				"title": "Already Done Task",
				"property": prop.name,
				"maintenance_type": "One-off",
				"status": "Completed",
				"scheduled_date": add_days(today(), 3),
				"completed_date": today(),
			}
		).insert(ignore_permissions=True)

		send_maintenance_reminders()
		# The mock may be called for tasks from OTHER test setups.
		# Check that it was NOT called for THIS property's task specifically.
		for call_args in mock_notify.call_args_list:
			self.assertNotIn(
				"Already Done Task",
				call_args.kwargs.get("message", ""),
			)
