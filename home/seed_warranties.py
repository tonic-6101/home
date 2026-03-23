# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Seed script: creates 10 example warranties for existing items.

Usage (inside the Docker container):
    bench --site home.localhost execute home.seed_warranties.seed

Prerequisites: items must already exist (run seed_appliances first).
"""

import frappe


# (item_name, warranty_type, provider, start_date, end_date, notes)
EXAMPLES = [
    (
        "Kühlschrank", "Manufacturer", "Liebherr",
        "2023-04-01", "2025-04-01",
        "2-year manufacturer warranty. Covers compressor and sealed system.",
    ),
    (
        "Waschmaschine", "Manufacturer", "Bosch",
        "2023-06-15", "2025-06-15",
        "2-year manufacturer warranty. Covers motor, drum, and electronics.",
    ),
    (
        "Waschmaschine", "Extended", "MediaMarkt Plus",
        "2025-06-16", "2028-06-15",
        "3-year extended warranty. Purchased at point of sale for €149.",
    ),
    (
        "Geschirrspüler", "Manufacturer", "Miele",
        "2024-01-10", "2026-01-10",
        "Standard 2-year Miele warranty. Motor warranted for 5 years separately.",
    ),
    (
        "Geschirrspüler", "Extended", "Miele Care",
        "2026-01-11", "2029-01-10",
        "3-year extended motor warranty from Miele. Purchased separately.",
    ),
    (
        "Heizkessel", "Manufacturer", "Viessmann",
        "2021-11-15", "2026-11-15",
        "5-year warranty conditional on annual service by certified installer.",
    ),
    (
        "Klimaanlage Wohnzimmer", "Manufacturer", "Daikin",
        "2024-03-20", "2027-03-20",
        "3-year manufacturer warranty. Compressor warranted for 5 years.",
    ),
    (
        "Fernseher", "Insurance", "Wertgarantie",
        "2024-11-25", "2029-11-25",
        "5-year accidental damage insurance. €100 excess per claim.",
    ),
    (
        "Backofen", "Manufacturer", "Siemens",
        "2024-05-01", "2026-05-01",
        "2-year standard warranty. Does not cover glass door or accessories.",
    ),
    (
        "Kaffeemaschine", "Manufacturer", "De'Longhi",
        "2024-08-10", "2026-08-10",
        "2-year manufacturer warranty. Covers brewing unit and grinder.",
    ),
]


def seed():
    """Create 10 example warranties attached to existing items."""

    # Find the household's single property.
    # Use creation desc to match the frontend's useProperty composable,
    # which picks the most recently created property.
    prop = frappe.get_all(
        "Home Property",
        filters={"is_archived": 0},
        fields=["name", "household"],
        order_by="creation desc",
        limit=1,
    )
    if not prop:
        print("No Home Property found — create a property first.")
        return

    property_name = prop[0]["name"]
    household = prop[0]["household"]

    # Build item_name → item ID lookup for this property
    items = frappe.get_all(
        "Home Item",
        filters={"property": property_name},
        fields=["name", "item_name"],
    )
    item_map = {a["item_name"]: a["name"] for a in items}

    created = 0
    for item_name, w_type, provider, w_start, w_end, notes in EXAMPLES:
        item_id = item_map.get(item_name)
        if not item_id:
            print(f"Skipping — item '{item_name}' not found on {property_name}")
            continue

        if frappe.db.exists("Home Warranty", {
            "item": item_id,
            "warranty_type": w_type,
        }):
            print(f"Skipping — {w_type} warranty already exists for {item_name}")
            continue

        doc = frappe.get_doc({
            "doctype": "Home Warranty",
            "household": household,
            "property": property_name,
            "item": item_id,
            "warranty_type": w_type,
            "provider": provider,
            "start_date": w_start,
            "end_date": w_end,
            "notes": notes,
        })
        doc.insert(ignore_permissions=True)
        created += 1
        print(f"Created {doc.name} — {w_type} warranty for {item_name}")

    frappe.db.commit()
    print(f"\nDone — {created} warranties created.")
