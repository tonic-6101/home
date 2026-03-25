# Architecture

## Layer model

```
Layer 0   Frappe Core        (Contact, File, Event, User...)
Layer 1   Dock               coordination layer
Layer 2   Home               household management — you are here
Layer 3   Service Apps       (Drive, Repo, Jana)
```

Home is a **Layer 2 domain app**. It depends on Dock for the top bar, search, notifications, settings UI, and guest portal. All household data is self-contained — Home never writes to Dock DocTypes directly; it uses Dock's hook system to register capabilities.

## Permission model

All Home data is scoped to a household. Users only see records belonging to households they are members of.

### Role hierarchy

```
Owner   >   Adult   >   Child
```

| Capability | Owner | Adult | Child |
|------------|-------|-------|-------|
| View properties and rooms | Yes | Yes | Yes |
| View items and maintenance | Yes | Yes | Yes |
| Create/edit properties | Yes | Yes | No |
| Create/edit items | Yes | Yes | No |
| Complete maintenance tasks | Yes | Yes | No |
| View financial data (budgets, mortgages, insurance, bills, equity) | Yes | Yes | No |
| Delete records | Yes | No | No |
| Manage household members | Yes | No | No |
| Archive/unarchive properties | Yes | No | No |
| Configure Home Settings | Yes | No | No |

Financial data visibility is enforced at the API layer. Child-role users receive empty results from financial endpoints, not permission errors.

## DocTypes

Home defines 27 DocTypes:

| DocType | Type | Purpose |
|---------|------|---------|
| Home Settings | Single | App-wide configuration (alert thresholds, lifespan defaults, preferences) |
| Home Household | Document | Top-level scope for all home data |
| Home Household Member | Child table | User-to-household mapping with role (Owner/Adult/Child) |
| Home Property | Document | Physical dwelling — house, apartment, unit |
| Home Room | Document | Room within a property |
| Home Item | Document | Physical item tracked in the household |
| Home Item Category Lifespan | Document | Expected lifespan by item category |
| Home Item Recall | Document | Product recall notices matched to items |
| Home Maintenance | Document | Scheduled or ad-hoc maintenance tasks |
| Home Maintenance Template | Document | Reusable maintenance schedules |
| Home Warranty | Document | Warranty coverage for items or property |
| Home Warranty Claim | Child table | Claims filed against a warranty |
| Home Utility Bill | Document | Monthly utility bills (electric, gas, water, etc.) |
| Home Insurance Policy | Document | Property or contents insurance policies |
| Home Insurance Claim | Document | Claims filed against an insurance policy |
| Home Budget | Document | Household budget with line items |
| Home Budget Line | Child table | Individual budget line item |
| Home Mortgage | Document | Mortgage/loan tracking |
| Home Purchase Return | Document | Product returns and refunds |
| Home Equity Snapshot | Document | Point-in-time property value records |
| Home Emergency Contact | Document | Emergency contacts for a property |
| Home Moving Task | Document | Tasks for property moves |
| Home Photo | Document | Photos attached to properties, rooms, or items |
| Home Letter Template | Document | Templates for correspondence (complaints, requests) |
| Home Generated Letter | Document | Rendered correspondence from templates |
| Home Improvement Wish | Document | Wishlist items for property improvements |
| Home Repair Fund | Virtual | Calculated from budget allocations (no DocType — API only) |

## Build outputs

Home's Vite config produces two entry points:

| Entry | File | Purpose |
|-------|------|---------|
| SPA app | `home-app.js` | Full Home SPA at `/home/*` |
| Settings ESM | `home-settings.esm.js` | Settings panel loaded by Dock Settings UI |

The SPA imports `DockNavbar` and `DockLayout` from Dock's ESM bundle for a consistent shell experience.

## Soft integrations

Home does not hard-depend on any app other than Dock. The following integrations activate when the target app is installed:

| App | Integration | Direction |
|-----|-------------|-----------|
| Orga | Maintenance tasks can link to Orga projects | Home reads |
| Jana | OCR extraction from item photos, AI-powered insights (health score suggestions, recall matching) | Home calls Jana API |
| Frame (Dock guest portal) | Property guest view — shareable read-only property summary | Home registers via `frame_guest_pages` hook |
| Mesa / Rent | Budget soft lines for business-related expenses | Home reads aggregates if available |

All integrations check for app presence at runtime before attempting any cross-app call. If the target app is absent, the feature is silently disabled.
