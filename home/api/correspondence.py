# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Letter template and correspondence API.

Renders Jinja2 letter templates pre-filled from Home DocType records
(warranty, maintenance, utility bill, insurance policy) and exports
the result as PDF via WeasyPrint.
"""

import frappe
from frappe import _
from jinja2 import Environment, BaseLoader, Undefined

from home.api.permission import require_household_access, require_role


class _BracketUndefined(Undefined):
	"""Render missing template variables as [VARIABLE NAME] instead of empty string."""

	def __str__(self):
		return f"[{self._undefined_name.upper().replace('_', ' ')}]"


@frappe.whitelist()
def get_templates() -> dict:
	"""List all letter templates (system and custom), grouped by situation type.

	Returns:
		dict with ``templates`` list.
	"""
	templates = frappe.get_all(
		"Home Letter Template",
		fields=[
			"name", "template_name", "situation_type",
			"context_doctype", "notes", "is_system_template",
		],
		order_by="situation_type asc, template_name asc",
	)
	return {"templates": templates}


@frappe.whitelist()
def render_draft(
	template: str,
	context_doctype: str = "",
	context_name: str = "",
	property: str = "",
) -> dict:
	"""Render a letter template with data from source records.

	Resolves Jinja2 placeholders against the property, logged-in user,
	and the selected context record. Unfilled placeholders appear as
	``[VARIABLE NAME]`` in the rendered output.

	Args:
		template: Name of the Home Letter Template record.
		context_doctype: DocType providing context (e.g. "Home Warranty").
		context_name: Name of the context record.
		property: Name of the Home Property record.

	Returns:
		dict with rendered ``subject`` and ``body``.
	"""
	doc_template = frappe.get_doc("Home Letter Template", template)
	prop = frappe.get_doc("Home Property", property)
	require_household_access(prop.household)
	require_role(prop.household, "Adult")

	ctx = _build_context(prop, context_doctype, context_name)

	env = Environment(loader=BaseLoader(), undefined=_BracketUndefined)
	subject = env.from_string(doc_template.subject_template).render(ctx)
	body = env.from_string(doc_template.body_template).render(ctx)

	return {
		"template": template,
		"template_name": doc_template.template_name,
		"subject": subject,
		"body": body,
	}


@frappe.whitelist()
def export_pdf(subject: str, body: str, property: str) -> None:
	"""Generate a print-ready PDF from a rendered letter via WeasyPrint.

	Sets the Frappe response to a file download (``letter-YYYY-MM-DD.pdf``).

	Args:
		subject: Rendered letter subject line.
		body: Rendered letter body (HTML).
		property: Name of the Home Property record (for access check).
	"""
	from frappe.utils import today

	doc = frappe.get_doc("Home Property", property)
	require_household_access(doc.household)
	require_role(doc.household, "Adult")

	html = f"""
	<html><body style="font-family: Georgia, serif; max-width: 720px; margin: 40px auto; font-size: 13pt; line-height: 1.6;">
	<h2 style="font-size: 14pt; font-weight: normal;">{frappe.utils.escape_html(subject)}</h2>
	<div>{body}</div>
	</body></html>
	"""
	pdf_bytes = frappe.utils.pdf.get_pdf(html)

	filename = f"letter-{today()}.pdf"
	frappe.local.response.filename = filename
	frappe.local.response.filecontent = pdf_bytes
	frappe.local.response.type = "download"


def _build_context(prop, context_doctype: str, context_name: str) -> dict:
	"""Build the Jinja2 template context from property, user, and source record.

	Always includes: property_address, today, sender_name, sender_email.
	Additional fields depend on ``context_doctype``:
	- Home Warranty: appliance + warranty fields
	- Home Maintenance: job + contractor fields
	- Home Utility Bill: utility bill fields
	- Home Insurance Policy: policy fields
	"""
	from frappe.utils import today, formatdate

	user = frappe.session.user
	user_doc = frappe.get_doc("User", user)

	address_parts = filter(None, [
		prop.address_line1, prop.address_line2,
		prop.postal_code, prop.city,
	])
	ctx = {
		"property_address": ", ".join(address_parts),
		"today": formatdate(today(), "d MMMM yyyy"),
		"sender_name": user_doc.full_name,
		"sender_email": user_doc.email,
	}

	if not context_doctype or not context_name:
		return ctx

	source = frappe.get_doc(context_doctype, context_name)

	if context_doctype == "Home Warranty":
		item = frappe.get_doc("Home Item", source.item) if source.item else None
		ctx.update({
			"item_name": item.item_name if item else "",
			"brand": item.brand if item else "",
			"model": item.model if item else "",
			"serial_number": item.serial_number if item else "",
			"purchase_date": formatdate(item.purchase_date, "d MMMM yyyy") if (item and item.purchase_date) else "",
			"purchase_price": f"\u20ac{item.purchase_price:,.0f}" if (item and item.purchase_price) else "",
			"warranty_type": source.warranty_type,
			"warranty_provider": source.provider or "",
			"warranty_end_date": formatdate(source.end_date, "d MMMM yyyy") if source.end_date else "",
			"claim_date": formatdate(today(), "d MMMM yyyy"),
		})

	elif context_doctype == "Home Maintenance":
		contractor_name = ""
		if source.contractor:
			contractor_name = frappe.db.get_value("Contact", source.contractor, "full_name") or ""
		ctx.update({
			"job_title": source.title,
			"job_date": formatdate(source.scheduled_date, "d MMMM yyyy") if source.scheduled_date else "",
			"completed_date": formatdate(source.completed_date, "d MMMM yyyy") if source.completed_date else "",
			"cost_paid": f"\u20ac{source.cost:,.0f}" if source.cost else "",
			"contractor_name": contractor_name,
		})

	elif context_doctype == "Home Utility Bill":
		ctx.update({
			"utility_type": source.bill_type,
			"provider": source.provider or "",
			"period_start": formatdate(source.period_start, "d MMMM yyyy") if source.period_start else "",
			"period_end": formatdate(source.period_end, "d MMMM yyyy") if source.period_end else "",
			"amount_billed": f"\u20ac{source.amount:,.2f}" if source.amount else "",
			"reading_start": source.reading_start or "",
			"reading_end": source.reading_end or "",
		})

	elif context_doctype == "Home Insurance Policy":
		ctx.update({
			"policy_name": source.policy_name,
			"policy_type": source.policy_type,
			"provider": source.provider,
			"policy_number": source.policy_number or "",
			"coverage_amount": f"\u20ac{source.coverage_amount:,.0f}" if source.coverage_amount else "",
		})

	return ctx
