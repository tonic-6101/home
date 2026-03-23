# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_years, today

from home.api.repair_fund import get_repair_fund


class TestRepairFund(FrappeTestCase):
    def _setup(self):
        hh = frappe.get_doc(
            {
                "doctype": "Home Household",
                "household_name": "Repair Fund Test Household",
                "members": [
                    {"display_name": "Owner", "role": "Owner", "user": "Administrator"},
                ],
            }
        ).insert(ignore_permissions=True)

        prop = frappe.get_doc(
            {
                "doctype": "Home Property",
                "household": hh.name,
                "property_name": "Repair Fund Test Property",
                "property_type": "House",
                "ownership_status": "Owner-occupied",
            }
        ).insert(ignore_permissions=True)

        return hh, prop

    def test_repair_fund_with_purchase_price(self):
        """Property purchased 5 years ago for 300000: rate=0.01, annual_target=3000, basis=purchase_price."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        prop.purchase_price = 300000
        prop.purchase_date = add_years(today(), -5)
        prop.save(ignore_permissions=True)

        result = get_repair_fund(property=prop.name)

        self.assertEqual(result.get("rate"), 0.01)
        self.assertEqual(result.get("annual_target"), 3000)
        self.assertEqual(result.get("basis"), "purchase_price")

    def test_repair_fund_area_fallback(self):
        """No purchase price but area_sqm=100: basis should be area_estimate."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        prop.purchase_price = 0
        prop.purchase_date = add_years(today(), -5)
        prop.area_sqm = 100
        prop.save(ignore_permissions=True)

        result = get_repair_fund(property=prop.name)

        self.assertEqual(result.get("basis"), "area_estimate")

    def test_repair_fund_no_data(self):
        """No purchase date: verify null result with message."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        prop.purchase_price = 0
        prop.purchase_date = None
        prop.area_sqm = 0
        prop.save(ignore_permissions=True)

        result = get_repair_fund(property=prop.name)

        self.assertIsNone(result.get("annual_target"))
        self.assertIsNotNone(result.get("message"))
