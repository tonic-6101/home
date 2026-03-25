# Installation

## Requirements

| Component | Minimum Version |
|-----------|----------------|
| Frappe | 16.0+ |
| Python | 3.14+ |
| Node.js | 24+ |
| MariaDB | 10.6+ |
| Dock | 0.3.0+ |

Home requires both `frappe` and `dock` as installed apps.

## Install via bench

```bash
# Inside the Frappe bench container:
bench get-app https://github.com/tonic-6101/home.git
bench --site your-site.localhost install-app home
bench --site your-site.localhost migrate
bench build --app home
```

## Initial setup

### 1. Create your first household

After installation, navigate to `/home` in your browser. The onboarding wizard prompts you to create a household. A household is the top-level scope for all Home data — every property, item, budget, and member belongs to exactly one household.

### 2. Add a property

Each household needs at least one property. A property represents a physical dwelling (house, apartment, unit). You can manage multiple properties under a single household.

### 3. Invite members

Invite other users to your household via **Household Settings > Members**. Each member is assigned a role that controls what they can see and do.

## Roles

Home defines two Frappe roles that map to a three-tier household hierarchy:

| Frappe Role | Household Role | Capabilities |
|-------------|---------------|--------------|
| Home Manager | Owner | Full access. Create/delete properties, manage members, view all financial data, configure settings. |
| Home User | Adult | Read/write access to properties, items, maintenance, warranties. Can view financial data. Cannot delete properties or manage household members. |
| Home User | Child | Read-only access to non-financial data. Cannot view budgets, mortgages, insurance policies, utility bills, or equity snapshots. Cannot delete any records. |

The household role (Owner / Adult / Child) is stored on the `Home Household Member` record. The Frappe role controls DocType-level permissions; the household role adds row-level filtering.

## Update

```bash
cd apps/home
git pull upstream develop
bench --site your-site.localhost migrate
bench build --app home
```

Always run `migrate` after pulling — DocType schema changes require it.

## Uninstall

```bash
bench --site your-site.localhost uninstall-app home
bench remove-app home
```

This removes all Home DocTypes and their data from the site database. The operation is irreversible.
