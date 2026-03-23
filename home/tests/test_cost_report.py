# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.cost_report import get_cost_report


class TestCostReport(FrappeTestCase):
    def _setup(self):
        hh = frappe.get_doc(
            {
                "doctype": "Home Household",
                "household_name": "Cost Report Test Household",
                "members": [
                    {"display_name": "Owner", "role": "Owner", "user": "Administrator"},
                ],
            }
        ).insert(ignore_permissions=True)

        prop = frappe.get_doc(
            {
                "doctype": "Home Property",
                "household": hh.name,
                "property_name": "Cost Report Test Property",
                "property_type": "House",
                "ownership_status": "Owner-occupied",
            }
        ).insert(ignore_permissions=True)

        return hh, prop

    def test_cost_report_aggregates(self):
        """Create maintenance (cost=500) and utility bill (amount=100) in 2025, verify aggregates."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        # Create a completed maintenance task with cost
        frappe.get_doc(
            {
                "doctype": "Home Maintenance",
                "property": prop.name,
                "title": "Cost Report Test Repair",
                "category": "Plumbing",
                "maintenance_type": "One-off",
                "status": "Completed",
                "scheduled_date": "2025-06-15",
                "completed_date": "2025-06-15",
                "cost": 500,
            }
        ).insert(ignore_permissions=True)

        # Create a utility bill
        frappe.get_doc(
            {
                "doctype": "Home Utility Bill",
                "property": prop.name,
                "bill_type": "Electricity",
                "period_start": "2025-06-01",
                "period_end": "2025-06-30",
                "amount": 100,
            }
        ).insert(ignore_permissions=True)

        result = get_cost_report(property=prop.name, year=2025)

        self.assertEqual(result.get("total_spend"), 600)
        self.assertEqual(result.get("record_count"), 2)

        categories = result.get("by_category", {})
        self.assertGreaterEqual(len(categories), 2)

    def test_cost_report_empty_year(self):
        """Query a year with no data: total_spend=0, record_count=0."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        result = get_cost_report(property=prop.name, year=2010)

        self.assertEqual(result.get("total_spend"), 0)
        self.assertEqual(result.get("record_count"), 0)
