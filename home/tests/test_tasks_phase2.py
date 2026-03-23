# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for Phase 2 scheduled tasks: insurance renewal alerts and unpaid bill reminders."""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from home.tasks import send_insurance_renewal_alerts, send_unpaid_bill_reminders


class TestInsuranceRenewalAlerts(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Insurance Alert Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Insurance Alert Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	@patch("home.tasks._send_notification")
	def test_insurance_renewal_alert_fires(self, mock_notify):
		hh, prop = self._setup()

		# Create an insurance policy expiring in exactly 60 days (default renewal_notice_days)
		frappe.get_doc(
			{
				"doctype": "Home Insurance Policy",
				"property": prop.name,
				"policy_name": "Home Insurance Test",
				"policy_type": "Buildings",
				"provider": "Test Insurer",
				"start_date": "2020-01-01",
				"end_date": add_days(today(), 60),
				"renewal_notice_days": 60,
			}
		).insert(ignore_permissions=True)

		send_insurance_renewal_alerts()
		mock_notify.assert_called()


class TestUnpaidBillReminders(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Bill Reminder Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Bill Reminder Test House",
				"property_type": "Apartment",
				"ownership_status": "Rented",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	@patch("home.tasks._send_notification")
	def test_unpaid_bill_reminder_fires(self, mock_notify):
		hh, prop = self._setup()

		frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Electricity",
				"period_start": add_days(today(), -30),
				"period_end": add_days(today(), -1),
				"amount": 120.00,
				"due_date": add_days(today(), 3),
				"paid": 0,
			}
		).insert(ignore_permissions=True)

		send_unpaid_bill_reminders()
		mock_notify.assert_called()

	@patch("home.tasks._send_notification")
	def test_no_reminder_for_paid_bill(self, mock_notify):
		"""A paid bill should not trigger a reminder."""
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Paid Bill Test HH",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Paid Bill Test House",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Home Utility Bill",
				"property": prop.name,
				"bill_type": "Water",
				"period_start": add_days(today(), -30),
				"period_end": add_days(today(), -1),
				"amount": 45.00,
				"due_date": add_days(today(), 3),
				"paid": 1,
			}
		).insert(ignore_permissions=True)

		send_unpaid_bill_reminders()
		# The mock may be called for bills from OTHER test setups.
		# Check that it was NOT called for THIS property's bill specifically.
		for call_args in mock_notify.call_args_list:
			msg = call_args.kwargs.get("message", "")
			self.assertNotIn("Paid Bill Test House", msg)
