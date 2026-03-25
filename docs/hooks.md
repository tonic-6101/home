# Dock Integration Hooks

Home declares its Dock capabilities in `home/hooks.py`. Dock reads these at runtime — no import of Dock code is required.

---

## App Registry

```python
dock_app_registry = {
    "label": "Home",
    "icon": "house",
    "color": "#16A34A",
    "route": "/home",
}
```

Registers Home in the Dock top bar app switcher.

---

## Settings Sections

```python
dock_settings_sections = [
    {
        "app": "home",
        "label": "Home",
        "icon": "house",
        "esm_bundle": "/assets/home/js/home-settings.esm.js",
        "sections": [
            {"key": "household", "label": "Household", "description": "Household name, address, and member defaults"},
            {"key": "alerts", "label": "Alerts", "description": "Notification thresholds for warranties, maintenance, and bills"},
            {"key": "lifespans", "label": "Lifespans", "description": "Default expected lifespans by item category"},
            {"key": "preferences", "label": "Preferences", "description": "Display and behavior preferences"},
        ],
    }
]
```

The settings ESM bundle is loaded by Dock's unified settings UI. Each subsection maps to a tab within the Home settings panel.

| Subsection | Controls |
|------------|----------|
| Household | Household display name, default address, member invitation defaults |
| Alerts | Days-before-expiry thresholds for warranty, insurance, and bill due notifications |
| Lifespans | Default expected lifespan per item category (used by health score calculations) |
| Preferences | Currency, date display, dashboard layout preferences |

---

## Search Sections

```python
dock_search_sections = [
    {
        "label": "Properties",
        "doctype": "Home Property",
        "search_fields": ["property_name", "address"],
    },
    {
        "label": "Items",
        "doctype": "Home Item",
        "search_fields": ["item_name", "brand", "model", "serial_number", "barcode"],
    },
]
```

These register Home's searchable content with Dock's global search (Cmd+K). Properties are searched by name and address; items by name, brand, model, serial number, and barcode.

---

## Notification Types

```python
dock_notification_types = [
    {"type": "warranty_expiring", "label": "Warranty Expiring", "icon": "shield-alert"},
    {"type": "maintenance_due", "label": "Maintenance Due", "icon": "wrench"},
    {"type": "insurance_renewal", "label": "Insurance Renewal", "icon": "file-shield"},
    {"type": "bill_due", "label": "Bill Due", "icon": "receipt"},
    {"type": "refund_overdue", "label": "Refund Overdue", "icon": "undo-2"},
    {"type": "recall_alert", "label": "Product Recall", "icon": "alert-triangle"},
    {"type": "equity_update", "label": "Equity Update", "icon": "trending-up"},
]
```

Home publishes notifications via `dock.api.notifications.publish` using these registered types. Each type appears in Dock's notification center with its own icon and filter category.

---

## Jana Permissions

```python
jana_permissions = [
    {"doctype": "Home Property", "actions": ["read", "search"]},
    {"doctype": "Home Item", "actions": ["read", "search"]},
    {"doctype": "Home Maintenance", "actions": ["read"]},
    {"doctype": "Home Warranty", "actions": ["read"]},
    {"doctype": "Home Utility Bill", "actions": ["read"], "label": "Financial Summary"},
]
```

Grants Jana (the AI assistant) scoped access to Home data. Jana can read and search properties and items, read maintenance and warranty records, and produce financial summaries from utility bill data. All access respects the user's household membership and role.

---

## Jana Search Providers

```python
jana_search_providers = [
    {"label": "Properties", "doctype": "Home Property", "search_fields": ["property_name", "address"]},
    {"label": "Items", "doctype": "Home Item", "search_fields": ["item_name", "brand", "model"]},
]
```

Registers Home content as searchable sources within Jana's conversational interface.

---

## Frame Guest Pages

```python
frame_guest_pages = [
    {
        "view_id": "home_property_guest",
        "label": "Property Summary",
        "source_doctype": "Home Property",
        "component_url": "/assets/home/js/home-app.js",
        "route": "/guest/home/property",
    },
]
```

Registers a guest-accessible property view with Dock's guest portal (Frame). When a user shares a property via guest link, the recipient sees a read-only summary including rooms, emergency contacts, and a property photo — without needing a Frappe account.
