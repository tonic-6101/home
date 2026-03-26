# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""
Migrate Home Maintenance records to Orga Tasks.

This patch:
1. Converts each Home Maintenance record into an Orga Task with Home custom fields.
2. Converts Home Maintenance Templates into Orga Task Templates.
3. Deletes the source DocTypes after migration.

Idempotent: skips records that appear to have already been migrated.
"""

import frappe
from frappe import _
from frappe.utils import today


STATUS_MAP = {
    "Scheduled": "Open",
    "In Progress": "In Progress",
    "Completed": "Completed",
    "Cancelled": "Cancelled",
}

SEASON_TO_CATEGORY = {
    "Spring": "Seasonal",
    "Autumn": "Seasonal",
    "Winter": "Seasonal",
    "Annual": "General",
    "Move-in": "Onboarding",
    "Custom": "Custom",
}


def execute():
    # Guard: only run if source DocTypes still exist
    if not frappe.db.exists("DocType", "Home Maintenance"):
        return

    if "orga" not in frappe.get_installed_apps():
        frappe.log_error(
            "Orga is not installed — cannot migrate Home Maintenance to Orga Tasks.",
            "Home Migration"
        )
        return

    _migrate_maintenance_records()
    _migrate_maintenance_templates()
    _cleanup_source_doctypes()


def _migrate_maintenance_records():
    """Convert Home Maintenance records to Orga Tasks."""
    records = frappe.get_all(
        "Home Maintenance",
        fields=[
            "name", "title", "property", "room", "item", "contractor",
            "category", "status", "maintenance_type", "recurrence",
            "scheduled_date", "completed_date", "cost", "notes",
            "household",
        ],
    )

    migrated = 0
    for rec in records:
        # Skip if already migrated (check by subject + home_property + start_date)
        existing = frappe.db.exists("Orga Task", {
            "subject": rec.title,
            "home_property": rec.property,
            "start_date": rec.scheduled_date,
        })
        if existing:
            continue

        task_data = {
            "doctype": "Orga Task",
            "subject": rec.title or _("Untitled Maintenance"),
            "status": STATUS_MAP.get(rec.status, "Open"),
            "start_date": rec.scheduled_date,
            "due_date": rec.scheduled_date,
            "completed_date": rec.completed_date,
            "actual_cost": rec.cost or 0,
            "description": rec.notes or "",
            "assigned_to": frappe.session.user,
            # Recurrence
            "is_recurring": 1 if rec.maintenance_type == "Recurring" else 0,
            "recurrence": rec.recurrence if rec.maintenance_type == "Recurring" else None,
            # Home custom fields
            "home_property": rec.property,
            "home_room": rec.room,
            "home_item": rec.item,
            "home_contractor": rec.contractor,
            "home_maintenance_category": rec.category,
        }

        try:
            doc = frappe.get_doc(task_data)
            doc.flags.ignore_permissions = True
            doc.insert()
            migrated += 1
        except Exception as e:
            frappe.log_error(
                f"Failed to migrate Home Maintenance {rec.name}: {e}",
                "Home Migration"
            )

    if migrated:
        frappe.db.commit()
        frappe.log_error(
            f"Migrated {migrated} Home Maintenance records to Orga Tasks.",
            "Home Migration (info)"
        )


def _migrate_maintenance_templates():
    """Convert Home Maintenance Templates to Orga Task Templates."""
    if not frappe.db.exists("DocType", "Home Maintenance Template"):
        return

    templates = frappe.get_all(
        "Home Maintenance Template",
        fields=["name", "template_name", "season", "description", "is_system_template"],
    )

    migrated = 0
    for tpl in templates:
        # Skip if already migrated
        existing = frappe.db.exists("Orga Task Template", {
            "template_name": tpl.template_name,
        })
        if existing:
            continue

        # Get template tasks
        tasks = frappe.get_all(
            "Home Maintenance Template Task",
            filters={"parent": tpl.name},
            fields=["title", "category", "days_offset", "notes"],
            order_by="idx asc",
        )

        tpl_data = {
            "doctype": "Orga Task Template",
            "template_name": tpl.template_name,
            "category": SEASON_TO_CATEGORY.get(tpl.season, "Custom"),
            "description": tpl.description or "",
            "is_system_template": tpl.is_system_template,
            "tasks": [],
        }

        for task in tasks:
            tpl_data["tasks"].append({
                "subject": task.title,
                "task_type": task.category or "",
                "priority": "Medium",
                "days_offset": task.days_offset or 0,
                "notes": task.notes or "",
            })

        try:
            doc = frappe.get_doc(tpl_data)
            doc.flags.ignore_permissions = True
            doc.flags.in_install = True  # Allow creating system templates
            doc.insert()
            migrated += 1
        except Exception as e:
            frappe.log_error(
                f"Failed to migrate template {tpl.name}: {e}",
                "Home Migration"
            )

    if migrated:
        frappe.db.commit()


def _cleanup_source_doctypes():
    """Delete Home Maintenance records and DocTypes after migration."""
    for dt in ("Home Maintenance Template Task", "Home Maintenance Template", "Home Maintenance"):
        if frappe.db.exists("DocType", dt):
            try:
                # Delete all records first
                frappe.db.delete(dt)
                frappe.db.commit()
                # Delete the DocType itself
                frappe.delete_doc("DocType", dt, force=True)
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(
                    f"Failed to delete DocType {dt}: {e}",
                    "Home Migration Cleanup"
                )
