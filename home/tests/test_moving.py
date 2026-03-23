# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.moving import (
    add_custom_task,
    generate_checklist,
    get_checklist,
    update_task_status,
)


class TestMovingWizard(FrappeTestCase):
    def _setup(self):
        hh = frappe.get_doc(
            {
                "doctype": "Home Household",
                "household_name": "Moving Test Household",
                "members": [
                    {"display_name": "Owner", "role": "Owner", "user": "Administrator"},
                ],
            }
        ).insert(ignore_permissions=True)

        prop = frappe.get_doc(
            {
                "doctype": "Home Property",
                "household": hh.name,
                "property_name": "Moving Test Property",
                "property_type": "House",
                "ownership_status": "Owner-occupied",
            }
        ).insert(ignore_permissions=True)

        return hh, prop

    def _all_tasks(self, result):
        """Flatten phase-grouped result into a single task list."""
        tasks = []
        for phase_data in result["phases"].values():
            tasks.extend(phase_data["tasks"])
        return tasks

    def test_generate_checklist(self):
        """Generate checklist and verify 23 system tasks are created, all status To do."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        generate_checklist(property=prop.name)
        result = get_checklist(property=prop.name)
        tasks = self._all_tasks(result)

        system_tasks = [t for t in tasks if t.get("is_system_task")]
        self.assertEqual(len(system_tasks), 23)

        for task in system_tasks:
            self.assertEqual(task.get("status"), "To do")

    def test_generate_checklist_idempotent(self):
        """Calling generate twice should throw an error."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        generate_checklist(property=prop.name)

        with self.assertRaises(frappe.ValidationError):
            generate_checklist(property=prop.name)

    def test_update_task_status(self):
        """Mark a task as Done, verify progress updates."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        generate_checklist(property=prop.name)
        result = get_checklist(property=prop.name)
        tasks = self._all_tasks(result)

        update_task_status(property=prop.name, idx=tasks[0]["idx"], status="Done")

        updated = get_checklist(property=prop.name)
        self.assertEqual(updated["done"], 1)

    def test_add_custom_task(self):
        """Add a custom task, verify it appears with is_system_task=0."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        generate_checklist(property=prop.name)
        add_custom_task(
            property=prop.name,
            title="Pack the cat toys",
            category="Other",
            phase="Before",
        )

        result = get_checklist(property=prop.name)
        tasks = self._all_tasks(result)
        custom = [t for t in tasks if t["title"] == "Pack the cat toys"]
        self.assertEqual(len(custom), 1)
        self.assertFalse(custom[0]["is_system_task"])

    def test_progress_excludes_skipped(self):
        """Skip 3 tasks, done 2 tasks, verify progress = 2 / (total - 3)."""
        hh, prop = self._setup()
        frappe.set_user("Administrator")

        generate_checklist(property=prop.name)
        result = get_checklist(property=prop.name)
        tasks = self._all_tasks(result)

        # Skip first 3 tasks
        for task in tasks[:3]:
            update_task_status(property=prop.name, idx=task["idx"], status="Skipped")

        # Complete next 2 tasks
        for task in tasks[3:5]:
            update_task_status(property=prop.name, idx=task["idx"], status="Done")

        updated = get_checklist(property=prop.name)
        self.assertEqual(updated["done"], 2)
        self.assertEqual(updated["skipped"], 3)
        expected_progress = 2 / (updated["total"] - 3)
        self.assertAlmostEqual(updated["progress"], expected_progress, places=4)
