# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Tests for Feature 6 — Barcode scan to register API endpoints."""

from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

from home.api.appliance import (
	_confidence,
	_extract_via_tesseract,
	_infer_category,
	check_recall,
	extract_from_image,
	lookup_barcode,
)


class TestInferCategory(FrappeTestCase):
	def test_white_goods(self):
		self.assertEqual(_infer_category("Bosch", "WAT28461 Washing Machine"), "White Goods")

	def test_hvac(self):
		self.assertEqual(_infer_category("Daikin", "FTXM25 Air Conditioner"), "HVAC")

	def test_heating(self):
		self.assertEqual(_infer_category("Vaillant", "ecoTEC Boiler"), "Heating")

	def test_kitchen(self):
		self.assertEqual(_infer_category("DeLonghi", "Espresso ECAM350"), "Kitchen")

	def test_electronics(self):
		self.assertEqual(_infer_category("Samsung", "QE55Q80T Television"), "Electronics")

	def test_plumbing(self):
		self.assertEqual(_infer_category("Grundfos", "ALPHA2 Pump"), "Plumbing")

	def test_unknown(self):
		self.assertEqual(_infer_category("Acme", "X100"), "")


class TestConfidence(FrappeTestCase):
	def test_high_confidence(self):
		self.assertEqual(_confidence("Bosch"), "high")

	def test_low_confidence_empty(self):
		self.assertEqual(_confidence(""), "low")

	def test_low_confidence_none(self):
		self.assertEqual(_confidence(None), "low")

	def test_low_confidence_short(self):
		self.assertEqual(_confidence("A"), "low")


class TestExtractViaTesseract(FrappeTestCase):
	@patch("home.api.appliance.pytesseract", create=True)
	@patch("home.api.appliance.Image", create=True)
	def test_extracts_brand_from_label(self, mock_image_mod, mock_tesseract):
		"""Tesseract OCR correctly extracts brand from 'Brand: Bosch' line."""
		import base64

		mock_img = MagicMock()
		mock_image_mod.open.return_value = mock_img
		mock_tesseract.image_to_string.return_value = (
			"Brand: Bosch\nModel: WAT28461\nSerial: WS1234567890\n"
		)

		# Minimal valid PNG (1x1 pixel)
		dummy_b64 = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50).decode()

		with patch.dict("sys.modules", {"pytesseract": mock_tesseract, "PIL": MagicMock(), "PIL.Image": mock_image_mod}):
			result = _extract_via_tesseract(dummy_b64)

		self.assertEqual(result["brand"], "Bosch")
		self.assertEqual(result["model"], "WAT28461")
		self.assertEqual(result["serial_number"], "WS1234567890")
		self.assertEqual(result["confidence"]["brand"], "high")

	def test_graceful_without_tesseract(self):
		"""When pytesseract is not installed, returns empty fields."""
		import base64

		dummy_b64 = base64.b64encode(b"fake image data").decode()
		result = _extract_via_tesseract(dummy_b64)

		self.assertEqual(result["brand"], "")
		self.assertEqual(result["model"], "")
		self.assertEqual(result["serial_number"], "")
		self.assertEqual(result["method"], "tesseract")


class TestScanEndpoints(FrappeTestCase):
	def _setup(self):
		hh = frappe.get_doc(
			{
				"doctype": "Home Household",
				"household_name": "Scan Test Household",
				"members": [
					{"display_name": "Owner", "role": "Owner", "user": "Administrator"},
				],
			}
		).insert(ignore_permissions=True)

		prop = frappe.get_doc(
			{
				"doctype": "Home Property",
				"household": hh.name,
				"property_name": "Scan Test Property",
				"property_type": "House",
				"ownership_status": "Owner-occupied",
			}
		).insert(ignore_permissions=True)

		return hh, prop

	def test_extract_from_image_returns_dict(self):
		"""extract_from_image returns a dict with expected keys."""
		hh, prop = self._setup()
		frappe.set_user("Administrator")

		import base64
		dummy_b64 = base64.b64encode(b"fake image data").decode()

		result = extract_from_image(image_b64=dummy_b64, property=prop.name)

		self.assertIn("brand", result)
		self.assertIn("model", result)
		self.assertIn("serial_number", result)
		self.assertIn("category", result)
		self.assertIn("confidence", result)
		self.assertIn("method", result)

	@patch("home.api.appliance.requests")
	def test_lookup_barcode_found(self, mock_requests):
		"""lookup_barcode returns product info when UPCitemdb has a match."""
		hh, prop = self._setup()
		frappe.set_user("Administrator")

		mock_response = MagicMock()
		mock_response.ok = True
		mock_response.json.return_value = {
			"items": [
				{
					"brand": "Bosch",
					"model": "WAT28461",
					"title": "Bosch WAT28461 Washing Machine",
				}
			]
		}
		mock_requests.get.return_value = mock_response

		result = lookup_barcode(barcode="4242002850580", property=prop.name)

		self.assertTrue(result["found"])
		self.assertEqual(result["brand"], "Bosch")
		self.assertEqual(result["model"], "WAT28461")

	@patch("home.api.appliance.requests")
	def test_lookup_barcode_not_found(self, mock_requests):
		"""lookup_barcode returns found=False when product not in database."""
		hh, prop = self._setup()
		frappe.set_user("Administrator")

		mock_response = MagicMock()
		mock_response.ok = True
		mock_response.json.return_value = {"items": []}
		mock_requests.get.return_value = mock_response

		result = lookup_barcode(barcode="0000000000000", property=prop.name)

		self.assertFalse(result["found"])

	@patch("home.api.appliance.requests")
	def test_lookup_barcode_api_failure(self, mock_requests):
		"""lookup_barcode degrades gracefully on API failure."""
		hh, prop = self._setup()
		frappe.set_user("Administrator")

		mock_requests.get.side_effect = Exception("Connection timeout")

		result = lookup_barcode(barcode="1234567890123", property=prop.name)

		self.assertFalse(result["found"])

	@patch("home.api.appliance.requests")
	def test_check_recall_found(self, mock_requests):
		"""check_recall returns recall info when RAPEX has a match."""
		mock_response = MagicMock()
		mock_response.ok = True
		mock_response.json.return_value = {
			"results": [
				{
					"productName": "Bosch Dishwasher Fire Risk",
					"url": "https://example.com/recall/1",
				}
			]
		}
		mock_requests.get.return_value = mock_response

		result = check_recall(brand="Bosch", model="SMS46GI55E")

		self.assertTrue(result["recall_found"])
		self.assertEqual(result["title"], "Bosch Dishwasher Fire Risk")

	@patch("home.api.appliance.requests")
	def test_check_recall_not_found(self, mock_requests):
		"""check_recall returns recall_found=False when no match."""
		mock_response = MagicMock()
		mock_response.ok = True
		mock_response.json.return_value = {"results": []}
		mock_requests.get.return_value = mock_response

		result = check_recall(brand="Bosch", model="WAT28461")

		self.assertFalse(result["recall_found"])

	def test_check_recall_empty_inputs(self):
		"""check_recall returns recall_found=False when both brand and model empty."""
		result = check_recall(brand="", model="")
		self.assertFalse(result["recall_found"])

	@patch("home.api.appliance.requests")
	def test_check_recall_api_failure(self, mock_requests):
		"""check_recall silently degrades on API failure."""
		mock_requests.get.side_effect = Exception("RAPEX timeout")

		result = check_recall(brand="Bosch", model="WAT28461")

		self.assertFalse(result["recall_found"])

	def test_extract_requires_household_access(self):
		"""extract_from_image raises PermissionError for non-member."""
		hh, prop = self._setup()

		# Create a user who is NOT a household member
		if not frappe.db.exists("User", "scan_outsider@test.local"):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": "scan_outsider@test.local",
					"first_name": "Outsider",
					"roles": [{"role": "Home User"}],
				}
			).insert(ignore_permissions=True)

		frappe.set_user("scan_outsider@test.local")

		import base64
		dummy_b64 = base64.b64encode(b"fake").decode()

		with self.assertRaises(frappe.PermissionError):
			extract_from_image(image_b64=dummy_b64, property=prop.name)

		frappe.set_user("Administrator")
