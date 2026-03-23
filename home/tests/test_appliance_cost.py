# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_years, today

from home.api.appliance_cost import get_item_cost


class TestApplianceCost(FrappeTestCase):
    def _setup(self):
        hh = frappe.get_doc(
            {
                "doctype": "Home Household",
                "household_name": "Item Cost Test Household",
                "members": [
                    {"display_name": "Owner", "role": "Owner", "user": "Administrator"},
                ],
            }
        ).insert(ignore_permissions=True)

        prop = frappe.get_doc(
            {
                "doctype": "Home Property",
                "household": hh.name,
                "property_name": "Item Cost Test Property",
                "property_type": "House",
                "ownership_status": "Owner-occupied",
            }
        ).insert(ignore_permissions=True)

        return hh, prop

    def test_appliance_cost_basic(self):
        """Appliance purchased 2 years ago for 1000, one maintenance of 200: lifetime_cost=1200, maintenance_share~16.7%."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        appliance = frappe.get_doc(
            {
                "doctype": "Home Item",
                "item_type": "Appliance",
                "property": prop.name,
                "item_name": "Cost Test Washing Machine",
                "category": "White Goods",
                "brand": "LG",
                "purchase_date": add_years(today(), -2),
                "purchase_price": 1000,
            }
        ).insert(ignore_permissions=True)

        # Create a maintenance record linked to this appliance
        frappe.get_doc(
            {
                "doctype": "Home Maintenance",
                "property": prop.name,
                "item": appliance.name,
                "title": "Item Cost Test Repair",
                "category": "General Repair",
                "maintenance_type": "One-off",
                "status": "Completed",
                "scheduled_date": today(),
                "completed_date": today(),
                "cost": 200,
            }
        ).insert(ignore_permissions=True)

        result = get_item_cost(item=appliance.name)

        self.assertEqual(result.get("lifetime_cost"), 1200)
        self.assertAlmostEqual(result.get("maintenance_share"), 200 / 1200 * 100, places=1)

    def test_appliance_cost_no_purchase_date(self):
        """No purchase date: age_years and cost_per_year should be None."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        appliance = frappe.get_doc(
            {
                "doctype": "Home Item",
                "item_type": "Appliance",
                "property": prop.name,
                "item_name": "Cost Test No Date Oven",
                "category": "Kitchen",
                "brand": "Samsung",
            }
        ).insert(ignore_permissions=True)

        result = get_item_cost(item=appliance.name)

        self.assertIsNone(result.get("age_years"))
        self.assertIsNone(result.get("cost_per_year"))
