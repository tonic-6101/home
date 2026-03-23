# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.settings import get_settings, reset_onboarding, save_settings


class TestSettingsAPI(FrappeTestCase):
    def _setup(self):
        hh = frappe.get_doc(
            {
                "doctype": "Home Household",
                "household_name": "Settings Test Household",
                "members": [
                    {"display_name": "Owner", "role": "Owner", "user": "Administrator"},
                ],
            }
        ).insert(ignore_permissions=True)

        prop = frappe.get_doc(
            {
                "doctype": "Home Property",
                "household": hh.name,
                "property_name": "Settings Test Property",
                "property_type": "House",
                "ownership_status": "Owner-occupied",
            }
        ).insert(ignore_permissions=True)

        return hh, prop

    def test_get_settings_lazy_init(self):
        """get_settings creates a record if none exists, verify defaults."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        result = get_settings(household=hh.name)

        self.assertIsNotNone(result)
        # Verify default warranty alert days are set
        self.assertIn("warranty_alert_days_1", result)

    def test_save_settings(self):
        """Change warranty_alert_days_1 to 60, verify it persists."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        # Ensure settings exist
        get_settings(household=hh.name)

        save_settings(household=hh.name, warranty_alert_days_1=60)

        result = get_settings(household=hh.name)
        self.assertEqual(result.get("warranty_alert_days_1"), 60)

    def test_reset_onboarding(self):
        """Set onboarding_tour_completed=1, reset, verify it's 0."""
        hh, _prop = self._setup()
        frappe.set_user("Administrator")

        # Set onboarding completed on the household member
        hh.members[0].onboarding_tour_completed = 1
        hh.save(ignore_permissions=True)
        self.assertEqual(hh.members[0].onboarding_tour_completed, 1)

        reset_onboarding(household=hh.name)

        hh.reload()
        self.assertEqual(hh.members[0].onboarding_tour_completed, 0)
