# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.onboarding import complete_onboarding, get_onboarding_status


class TestOnboarding(FrappeTestCase):
    def _setup(self):
        hh = frappe.get_doc(
            {
                "doctype": "Home Household",
                "household_name": "Onboarding Test Household",
                "members": [
                    {"display_name": "Owner", "role": "Owner", "user": "Administrator"},
                ],
            }
        ).insert(ignore_permissions=True)

        prop = frappe.get_doc(
            {
                "doctype": "Home Property",
                "household": hh.name,
                "property_name": "Onboarding Test Property",
                "property_type": "House",
                "ownership_status": "Owner-occupied",
            }
        ).insert(ignore_permissions=True)

        return hh, prop

    def test_onboarding_status_initial(self):
        """Verify tour_completed=False initially."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        result = get_onboarding_status(household=hh.name)

        self.assertFalse(result.get("tour_completed"))

    def test_complete_onboarding(self):
        """Complete onboarding, verify tour_completed=True."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        complete_onboarding(household=hh.name)

        result = get_onboarding_status(household=hh.name)
        self.assertTrue(result.get("tour_completed"))
