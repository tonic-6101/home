# Home

**Household Management for Frappe Framework**

[![Version](https://img.shields.io/badge/version-0.2.1-blue.svg)](https://github.com/tonic-6101/home/releases)
[![Frappe](https://img.shields.io/badge/frappe-v16+-green.svg)](https://frappeframework.com)
[![License](https://img.shields.io/badge/license-AGPL--3.0-orange.svg)](LICENSE)

<p align="center">
  <img src=".github/home-icon.svg" alt="Home" width="128">
</p>

Home is a comprehensive household management application built on the [Frappe Framework](https://frappeframework.com). Designed for homeowners and families who want to stay on top of their property, Home brings together maintenance scheduling, warranty tracking, insurance policies, budgeting, and inventory management in a single app.

---

## Features

### Property Management

Track your properties with health scores, room layouts, and repair fund monitoring.

- Property profiles with address, purchase date, and valuation
- Room-by-room organization
- Automatic property health scoring
- Repair fund tracking
- Property passport for a complete overview
- Guest access sharing via secure tokens

### Item Inventory

Keep a registry of everything in your household — appliances, furniture, electronics, and more.

- Item catalog with categories, purchase details, and locations
- Lifetime cost tracking and cost comparisons
- Appliance scanning for quick entry
- Category-based lifespan estimates
- Item recall monitoring with automated checks
- Photo gallery for visual documentation

### Maintenance Scheduling

Never miss a filter change, inspection, or seasonal task again.

- Create maintenance tasks with due dates and recurrence
- Reusable maintenance templates for common routines
- Daily reminders for upcoming and overdue tasks
- Task completion tracking
- Moving checklist for relocations

### Warranty Tracking

Know exactly what's covered and when coverage expires.

- Warranty records linked to items and properties
- Expiry alerts sent automatically
- Warranty claim management
- Document attachments for proof of purchase

### Insurance Policies

Manage all your insurance policies and claims in one place.

- Policy records with coverage details and renewal dates
- Renewal reminders before policies lapse
- Claim filing and tracking
- Policy export for sharing with agents

### Budget & Finance

Track household spending with budgets, utility bills, and equity snapshots.

- Create budgets with category-based line items
- Utility bill tracking with trend analysis
- Mortgage details and equity snapshots
- Cost reports across categories
- Purchase return and refund tracking with overdue alerts

### Household Management

Multi-user households with roles and emergency contacts.

- Create households and invite members
- Two roles: Home User and Home Manager
- All data scoped to household for privacy
- Emergency contact registry
- Wishlist for planned purchases

### Correspondence & Documents

Generate letters, store documents, and keep a paper trail.

- Letter templates for landlords, contractors, and insurers
- Generated letter history
- Document vault for important files
- Receipt storage

### Automated Alerts

Stay informed with scheduled notifications — no manual checking required.

- Warranty expiry alerts
- Maintenance due reminders
- Insurance renewal notices
- Unpaid bill reminders
- Overdue refund alerts
- Item recall notifications
- Equity update reminders

### Dock Integration

When [Dock](https://github.com/tonic-6101/dock) is installed, Home integrates into the ecosystem navigation and search.

- App registered in the Dock app switcher
- Properties and items searchable via Dock global search
- Settings accessible from Dock settings panel
- Notification types registered in Dock

### Jana AI Integration

When [Jana](https://github.com/tonic-6101/jana) is installed, Home exposes AI-powered tools for property insights, item lookups, maintenance summaries, warranty checks, and financial overviews.

---

## Installation

### Prerequisites

- Frappe Framework v16 or higher
- Python 3.14+
- Node.js 24+
- MariaDB 10.6+
- [Dock](https://github.com/tonic-6101/dock) (required dependency)

### Install via Bench

```bash
# Get the app
bench get-app home https://github.com/tonic-6101/home.git

# Install on your site
bench --site your-site.localhost install-app home

# Run migrations
bench --site your-site.localhost migrate

# Build assets
bench build --app home
```

### Access the Application

After installation, access Home at: `https://your-site.localhost/home`

---

## Quick Start

1. **Create a Household**: Set up your household and invite family members
2. **Add a Property**: Enter your property details — address, rooms, purchase info
3. **Register Items**: Add appliances and belongings with purchase dates and warranties
4. **Set Up Maintenance**: Create recurring maintenance tasks from templates
5. **Track Spending**: Set a budget and start logging utility bills
6. **Relax**: Home will notify you when something needs attention

---

## Technology Stack

- **Backend**: Frappe Framework, Python 3.14+
- **Frontend**: Vue 3, TypeScript, Tailwind CSS
- **UI Components**: FrappeUI
- **Database**: MariaDB
- **Build**: Vite

---

## Contributing

Contributions are welcome! This project uses `pre-commit` for code formatting and linting:

```bash
cd apps/home
pre-commit install
```

Pre-commit runs the following tools automatically:

- **ruff** — Python linting and formatting
- **eslint** — TypeScript/JavaScript linting
- **prettier** — Code formatting
- **pyupgrade** — Python syntax modernization

---

## Support

- **Issues**: [GitHub Issues](https://github.com/tonic-6101/home/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tonic-6101/home/discussions)

---

## License

GNU Affero General Public License v3.0 (AGPL-3.0)

See [LICENSE](LICENSE) for details.

```
SPDX-License-Identifier: AGPL-3.0-or-later
Copyright (C) 2024-2026 Tonic
```

---

## Acknowledgments

Built with [Frappe Framework](https://frappeframework.com) and [FrappeUI](https://github.com/frappe/frappe-ui).
