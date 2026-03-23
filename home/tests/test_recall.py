# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.recall import _match_recalls, dismiss_recall


class TestRecall(FrappeTestCase):
    def _setup(self):
        hh = frappe.get_doc(
            {
                "doctype": "Home Household",
                "household_name": "Recall Test Household",
                "members": [
                    {"display_name": "Owner", "role": "Owner", "user": "Administrator"},
                ],
            }
        ).insert(ignore_permissions=True)

        prop = frappe.get_doc(
            {
                "doctype": "Home Property",
                "household": hh.name,
                "property_name": "Recall Test Property",
                "property_type": "House",
                "ownership_status": "Owner-occupied",
            }
        ).insert(ignore_permissions=True)

        return hh, prop

    def test_match_recalls(self):
        """Create appliance with brand=Bosch, category=White Goods, verify correct recall filtering."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        appliance = frappe.get_doc(
            {
                "doctype": "Home Item",
                "item_type": "Appliance",
                "property": prop.name,
                "item_name": "Recall Test Dishwasher",
                "category": "White Goods",
                "brand": "Bosch",
            }
        ).insert(ignore_permissions=True)

        alerts = [
            {
                "recall_id": "RAPEX-2026-0001",
                "title": "Bosch Dishwasher Fire Risk",
                "brand": "Bosch",
                "category": "White Goods",
                "severity": "Serious",
                "published_date": "2026-01-15",
                "detail_url": "https://example.com/recall/1",
            },
            {
                "recall_id": "RAPEX-2026-0002",
                "title": "Samsung Fridge Coolant Leak",
                "brand": "Samsung",
                "category": "Kitchen",
                "severity": "High",
                "published_date": "2026-01-20",
                "detail_url": "https://example.com/recall/2",
            },
        ]

        matched = _match_recalls(appliance, alerts)

        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["recall_id"], "RAPEX-2026-0001")

    def test_dismiss_recall(self):
        """Add a recall child row to appliance, dismiss it, verify dismissed=1."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        appliance = frappe.get_doc(
            {
                "doctype": "Home Item",
                "item_type": "Appliance",
                "property": prop.name,
                "item_name": "Recall Dismiss Test Oven",
                "category": "Kitchen",
                "brand": "Miele",
            }
        ).insert(ignore_permissions=True)

        # Add a recall child row
        appliance.append(
            "recalls",
            {
                "recall_id": "RAPEX-2026-TEST",
                "title": "Miele Oven Handle Defect",
                "severity": "High",
                "dismissed": 0,
            },
        )
        appliance.save(ignore_permissions=True)

        recall_idx = appliance.recalls[0].idx

        dismiss_recall(item=appliance.name, recall_idx=recall_idx)

        appliance.reload()
        self.assertEqual(appliance.recalls[0].dismissed, 1)
