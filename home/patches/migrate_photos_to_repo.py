# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""
Migrate Home Photo records to Repo Explorer Entries.

This patch:
1. Ensures Home context custom fields exist on Explorer Entry.
2. Converts each Home Photo record into an Explorer Entry with Home custom fields.
3. Resolves before/after pair references in a second pass.
4. Deletes the source DocType after migration.

Idempotent: skips records that appear to have already been migrated.
"""

import frappe
from frappe import _


def execute():
	# Guard: only run if source DocType still exists
	if not frappe.db.exists("DocType", "Home Photo"):
		return

	if "repo" not in frappe.get_installed_apps():
		frappe.log_error(
			"Repo is not installed — cannot migrate Home Photo to Explorer Entry.",
			"Home Migration",
		)
		return

	# Ensure custom fields exist before migrating data
	from home.install import setup_repo_custom_fields

	setup_repo_custom_fields()

	_migrate_photo_records()
	_cleanup_source_doctype()


def _migrate_photo_records():
	"""Convert Home Photo records to Explorer Entries."""
	records = frappe.get_all(
		"Home Photo",
		fields=[
			"name",
			"photo",
			"property",
			"room",
			"item",
			"purpose",
			"photo_date",
			"before_after",
			"pair_ref",
			"caption",
			"notes",
			"owner",
			"creation",
		],
	)

	if not records:
		return

	# First pass: create Explorer Entries and build a mapping of old → new names
	old_to_new: dict[str, str] = {}
	migrated = 0

	for rec in records:
		# Determine the most specific object context
		if rec.item:
			object_type = "Home Item"
			object_name = _get_display_name("Home Item", rec.item, "item_name")
		elif rec.room:
			object_type = "Home Room"
			object_name = _get_display_name("Home Room", rec.room, "room_name")
		elif rec.property:
			object_type = "Home Property"
			object_name = _get_display_name("Home Property", rec.property, "property_name")
		else:
			object_type = "Other"
			object_name = rec.caption or _("Unnamed photo")

		# Skip if already migrated (check by home_property + captured_date + capture_purpose)
		captured_date = rec.photo_date or rec.creation
		existing = frappe.db.exists(
			"Explorer Entry",
			{
				"home_property": rec.property,
				"captured_date": captured_date,
				"capture_purpose": rec.purpose or "General",
				"object_name": object_name,
			},
		)
		if existing:
			old_to_new[rec.name] = existing
			continue

		# Resolve household from property
		household = None
		if rec.property:
			household = frappe.db.get_value("Home Property", rec.property, "household")

		entry_data = {
			"doctype": "Explorer Entry",
			"object_type": object_type,
			"object_name": object_name,
			"capture_purpose": rec.purpose or "General",
			"captured_date": captured_date,
			"captured_by": rec.owner,
			"processing_status": "Ready",
			"ai_summary": rec.caption or "",
			"tags": rec.notes or "",
			# Pairing — set pair_type now, resolve pair_ref in second pass
			"is_paired": 1 if rec.before_after else 0,
			"pair_type": rec.before_after or None,
			# Home custom fields
			"home_property": rec.property,
			"home_room": rec.room,
			"home_item": rec.item,
			"home_household": household,
		}

		try:
			doc = frappe.get_doc(entry_data)
			doc.flags.ignore_permissions = True
			doc.flags.skip_ai_processing = True
			doc.flags.skip_pair_sync = True
			doc.insert()

			old_to_new[rec.name] = doc.name
			migrated += 1

			# Copy the photo file attachment to the new Explorer Entry
			if rec.photo:
				_copy_attachment(rec.photo, "Explorer Entry", doc.name)

		except Exception as e:
			frappe.log_error(
				f"Failed to migrate Home Photo {rec.name}: {e}",
				"Home Photo Migration",
			)

	if migrated:
		frappe.db.commit()

	# Second pass: resolve pair_ref back-links
	pairs_linked = 0
	for rec in records:
		if not rec.pair_ref or rec.pair_ref not in old_to_new:
			continue

		new_name = old_to_new.get(rec.name)
		partner_name = old_to_new.get(rec.pair_ref)
		if not new_name or not partner_name:
			continue

		try:
			frappe.db.set_value(
				"Explorer Entry",
				new_name,
				"pair_ref",
				partner_name,
				update_modified=False,
			)
			pairs_linked += 1
		except Exception as e:
			frappe.log_error(
				f"Failed to link pair {new_name} → {partner_name}: {e}",
				"Home Photo Migration",
			)

	if pairs_linked:
		frappe.db.commit()

	frappe.log_error(
		f"Migrated {migrated} Home Photo records to Explorer Entries. "
		f"Linked {pairs_linked} before/after pairs.",
		"Home Photo Migration (info)",
	)


def _get_display_name(doctype: str, name: str, field: str) -> str:
	"""Get a human-readable display name, falling back to the record name."""
	try:
		return frappe.db.get_value(doctype, name, field) or name
	except Exception:
		return name


def _copy_attachment(file_url: str, to_doctype: str, to_name: str):
	"""Copy a Frappe File attachment to a new parent record."""
	if not file_url:
		return

	try:
		# Find the original File record
		existing_file = frappe.db.get_value(
			"File",
			{"file_url": file_url, "attached_to_doctype": "Home Photo"},
			["name", "file_name", "file_url", "is_private"],
			as_dict=True,
		)

		if not existing_file:
			# File might be attached differently — just create a reference
			frappe.get_doc(
				{
					"doctype": "File",
					"file_url": file_url,
					"attached_to_doctype": to_doctype,
					"attached_to_name": to_name,
					"is_private": 1,
				}
			).insert(ignore_permissions=True)
			return

		# Create a new File record pointing to the same file
		frappe.get_doc(
			{
				"doctype": "File",
				"file_url": existing_file.file_url,
				"file_name": existing_file.file_name,
				"attached_to_doctype": to_doctype,
				"attached_to_name": to_name,
				"is_private": existing_file.is_private,
			}
		).insert(ignore_permissions=True)

	except Exception as e:
		frappe.log_error(
			f"Failed to copy attachment {file_url} to {to_doctype}/{to_name}: {e}",
			"Home Photo Migration",
		)


def _cleanup_source_doctype():
	"""Delete Home Photo records and DocType after migration."""
	dt = "Home Photo"
	if not frappe.db.exists("DocType", dt):
		return

	try:
		frappe.db.delete(dt)
		frappe.db.commit()
		frappe.delete_doc("DocType", dt, force=True)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(
			f"Failed to delete DocType {dt}: {e}",
			"Home Photo Migration Cleanup",
		)
