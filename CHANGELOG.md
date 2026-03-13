# Changelog

## v0.1.0 — Community MVP

First release of Home — household management for Frappe.

### DocTypes (18)

- **Home Household** + Home Household Member — scoping anchor with Owner/Adult/Child roles
- **Home Property** + Home Emergency Contact + Home Equity Snapshot + Home Moving Task
- **Home Room** — rooms within a property
- **Home Appliance** + Home Appliance Recall — appliance tracking with category lifespan defaults
- **Home Warranty** + Home Warranty Claim — warranty records with expiry alerts
- **Home Maintenance** + Home Maintenance Template + Template Task — recurring maintenance with RECURRENCE_MAP
- **Home Contractor** — trusted tradespeople directory
- **Home Inventory Item** — household possessions with photo/receipt evidence
- **Home Purchase Return** — return tracking with refund status
- **Home Settings** + Home Appliance Category Lifespan — per-household configuration

### Features

- Household-scoped permissions: all data isolated per household
- Automatic lifespan population from category defaults on appliance creation
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
