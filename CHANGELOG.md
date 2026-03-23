# Changelog

## v0.2.0 — Community Complete

The analytical and household-life layer on top of Phase 1 data.

### New DocTypes (9)

- **Home Utility Bill** — track utility bills per property with cost spike detection
- **Home Insurance Policy** + Home Insurance Claim — insurance records with renewal alerts
- **Home Budget** + Home Budget Line — annual budget targets with read-time actuals
- **Home Mortgage** — mortgage records with equity snapshot triggers
- **Home Letter Template** — reusable letter templates with Jinja2 placeholders
- **Home Generated Letter** — saved correspondence generated from templates
- **Home Improvement Wish** — pre-commitment wishlist of desired improvements

### New Features

- **Household budget overview** — annual targets vs actual spend from maintenance, utilities, insurance
- **Home equity tracker** — property value minus mortgage balance, with snapshot history
- **Utility bill tracking** — bill log with cost spike detection (>150% of 12-month average)
- **Insurance policy management** — policies with configurable renewal alerts
- **Home health score** — computed 0–100 score from 8 deduction factors
- **Digital property passport** — chronological timeline of all property events
- **Household correspondence** — letter templates pre-filled from Home data (warranty claims, disputes)
- **Home improvement wishlist** — prioritised backlog with convert-to-maintenance action
- **Document vault** — read-only view layer over Frappe file attachments grouped by category
- **Insurance inventory export** — PDF/CSV export of inventory items for insurance claims
- **Budget target suggestions** — auto-seed from prior year actuals, 1% rule for maintenance

### New Scheduled Tasks

- Insurance renewal alerts (daily, per-policy configurable threshold)
- Unpaid bill reminders (daily, 3 days before due date)
- Overdue refund alerts (daily, re-alert at 14 days then every 7 days)
- Item recall monitoring (weekly, EU Safety Gate check — stub)
- Equity update reminders (daily, nudge when value >11 months stale)

### New API Endpoints

- `home.api.budget` — budget overview, target suggestions, category drill-down
- `home.api.equity` — equity tracker, value updates, manual snapshots
- `home.api.utility` — bill list with averages, quick-pay action
- `home.api.health` — health score computation
- `home.api.passport` — property passport timeline + PDF export
- `home.api.correspondence` — template rendering, PDF export
- `home.api.wishlist` — wishlist management, convert to maintenance
- `home.api.insurance_export` — PDF/CSV inventory export for insurance
- `home.api.document_vault` — file attachment grouped view
- `home.api.repair_fund` — repair fund calculator (1–2% rule, age-based rate)
- `home.api.cost_report` — annual cost report aggregation + CSV export
- `home.api.appliance_cost` — item lifetime cost metrics + comparison view
- `home.api.moving` — moving house wizard (23 system tasks, progress tracking)
- `home.api.recall` — item recall monitoring (dismiss, on-demand check)
- `home.api.settings` — per-household settings (get, save, lazy init)
- `home.api.onboarding` — guided onboarding tour status + completion
- `home.api.frame` — Frame guest portal (property overview via UUID token)
- `home.api.ical` — iCal subscription feed (per-property maintenance calendar)

### Property Controller

- Auto-generate iCal token on property creation
- Frame token auto-generated when Frame is installed
- `regenerate_frame_token()` and `regenerate_ical_token()` — Owner only

### Integrations

- Dock: 5 new notification types (insurance_renewal, bill_due, refund_overdue, recall_alert, equity_update)
- Jana: read access for 4 new DocTypes (Utility Bill, Insurance Policy, Budget, Mortgage)
- Mesa: soft budget line for groceries (read-only, invisible when absent)
- Rent: soft budget line for housing cost (read-only, invisible when absent)
- Frame: guest property overview via UUID token (auto-generated)
- iCal: per-property maintenance calendar subscription feed

### i18n

- 200+ German translations for all Phase 2 user-facing strings

---

## v0.1.0 — Community MVP

First release of Home — household management for Frappe.

### DocTypes (18)

- **Home Household** + Home Household Member — scoping anchor with Owner/Adult/Child roles
- **Home Property** + Home Emergency Contact + Home Equity Snapshot + Home Moving Task
- **Home Room** — rooms within a property
- **Home Item** + Home Item Recall — item tracking (appliances + possessions) with category lifespan defaults
- **Home Warranty** + Home Warranty Claim — warranty records with expiry alerts
- **Home Maintenance** + Home Maintenance Template + Template Task — recurring maintenance with RECURRENCE_MAP
- **Home Item** covers both appliances and household possessions with photo/receipt evidence
- **Home Purchase Return** — return tracking with refund status
- **Home Settings** + Home Item Category Lifespan — per-household configuration

### Features

- Household-scoped permissions: all data isolated per household
- Automatic lifespan population from category defaults on item creation
- Recurring maintenance: auto-creates next occurrence on completion
- Maintenance templates with "Spawn Tasks" API
- Warranty expiry alerts (daily scheduled task, configurable 90/30-day thresholds)
- Maintenance reminders (daily scheduled task, configurable days-before threshold)

### Integrations

- **Dock**: app registry, search sections, notification types
- **Jana**: read permissions, search providers
- **Tender**: create Tender Post from maintenance task
- **Orga**: create Orga Project from maintenance task
- **Frame**: guest property overview via UUID token
- **iCal**: per-property maintenance calendar subscription feed

### Roles

- Home User — standard household member
- Home Manager — household owner with full control

### i18n

- German translations (de.csv) for all user-facing strings
