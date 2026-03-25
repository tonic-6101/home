# Changelog

All notable changes to Home are documented here.

---

## 0.2.1

- Fix health score calculation not accounting for dismissed recalls
- Fix archived property check blocking read-only access
- Fix Child role receiving 403 instead of empty results on financial endpoints
- Improve guest portal token validation error messages
- Update Dock hook registration to match Dock 0.3.x settings API

## 0.2.0

- Add correspondence module (letter templates, rendered letters, PDF export)
- Add Home Improvement Wish DocType for property improvement tracking
- Add Home Maintenance Template for reusable maintenance schedules
- Add repair fund calculation endpoint
- Add equity snapshot history with appreciation percentage
- Add budget target suggestions based on historical spending
- Add OCR item extraction via Jana integration
- Add barcode lookup for item identification
- Add product recall checking and dismissal
- Add guest portal property view via Dock Frame integration
- Add Jana permissions and search provider hooks
- Expand health score to 8 deduction factors (was 5)
- Improve utility bill trend calculations with percentage changes

## 0.1.2

- Fix household member invitation not assigning correct Frappe role
- Fix utility bill mark_paid not updating status correctly
- Fix room item count including disposed items
- Add missing translation strings for German and French

## 0.1.1

- Fix Home Settings issingle flag not syncing after migrate
- Fix permission query conditions for multi-household users
- Improve onboarding flow for first-time users
- Add property dashboard endpoint with summary statistics

## 0.1.0

- Initial release
- Household management with Owner/Adult/Child role hierarchy
- Property and room tracking
- Item inventory with categories and lifespan tracking
- Maintenance task scheduling and completion
- Warranty tracking with expiry alerts
- Utility bill management with payment tracking
- Budget management with line items
- Insurance policy and claim tracking
- Mortgage tracking
- Equity snapshot recording
- Emergency contact management
- Moving task lists
- Photo attachments for properties, rooms, and items
- Dock integration: app registry, search sections, notification types, settings panel
- CSV and PDF export for item inventories
- Health score calculation for properties
