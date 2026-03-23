# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Seed script: creates 10 example possession items for development/demo.

Usage (inside the Docker container):
    bench --site home.localhost execute home.seed_inventory.seed

Prerequisites: at least one Home Property must exist (with rooms ideally).
"""

import frappe


EXAMPLES = [
    # (item_name, category, brand, model, serial_number, purchase_date, purchase_price, estimated_value, condition, insured, room_label, notes)
    (
        "Ledersofa 3-Sitzer", "Furniture", "Natuzzi", "Editions B845", None,
        "2022-03-15", 2400.00, 1800.00, "Good", False, "Living Room",
        "Italian leather, dark brown. Scotchgard-treated.",
    ),
    (
        "Esstisch Eiche massiv", "Furniture", "Team 7", "nox", None,
        "2021-08-20", 3200.00, 2800.00, "Excellent", False, "Dining Room",
        "Solid oak, 220×100 cm. Seats 8. Natural oil finish.",
    ),
    (
        "Ehering Gold 750", "Jewelry & Watches", "Niessing", "Aura", "NI-2019-4821",
        "2019-06-01", 1450.00, 1650.00, "Excellent", True, None,
        "18K yellow gold, 5 mm width. Engraved inside.",
    ),
    (
        "Rennrad", "Sports Equipment", "Canyon", "Ultimate CF SL 8", "WCR-2023-81204",
        "2023-04-10", 3499.00, 2800.00, "Good", True, None,
        "Carbon frame, Ultegra Di2 groupset. Size M.",
    ),
    (
        "Staubsauger-Roboter", "Electronics", "Roborock", "S8 MaxV Ultra", "RR-2024-55932",
        "2024-09-01", 1199.00, 1100.00, "New", False, "Utility Room",
        "LiDAR navigation, auto-empty dock, mop-washing station.",
    ),
    (
        "Akku-Bohrschrauber", "Tools & Equipment", "Festool", "TXS 18", "FT-2023-30214",
        "2023-11-05", 389.00, 350.00, "Good", False, None,
        "18V brushless, 2× 3.0 Ah batteries. In Systainer.",
    ),
    (
        "Gitarre Westerngitarre", "Musical Instruments", "Martin", "D-28", "MG-2020-17753",
        "2020-01-15", 2899.00, 3200.00, "Excellent", True, "Living Room",
        "Solid Sitka spruce top, East Indian rosewood back & sides.",
    ),
    (
        "Winterjacke Daunen", "Clothing & Accessories", "Canada Goose", "Expedition Parka", None,
        "2022-11-20", 1295.00, 900.00, "Good", False, "Bedroom",
        "Size L, black. 625 fill power duck down. Fur ruff.",
    ),
    (
        "Ölgemälde Landschaft", "Art & Collectibles", None, None, None,
        "2018-05-01", 850.00, 850.00, "Excellent", True, "Living Room",
        "Original oil painting, 80×60 cm. Signed by local artist. Framed.",
    ),
    (
        "Werkzeugkasten komplett", "Tools & Equipment", "Knipex / Wera", "Tool Check Plus Set", None,
        "2021-06-10", 420.00, 350.00, "Good", False, None,
        "39-piece set with Knipex pliers and Wera screwdrivers. In roll-up bag.",
    ),
]


def seed():
    """Create 10 example possession items on existing properties."""

    # Use creation desc to match the frontend's useProperty composable,
    # which picks the most recently created property.
    properties = frappe.get_all(
        "Home Property",
        filters={"is_archived": 0},
        fields=["name", "household"],
        order_by="creation desc",
        limit=2,
    )

    if not properties:
        print("No Home Property found — create a property first.")
        return

    primary = properties[0]
    secondary = properties[1] if len(properties) > 1 else properties[0]

    # First 8 items on primary property, last 2 on secondary
    assignments = [primary] * 8 + [secondary] * 2

    # Build room lookup: (property, room label) → room name
    rooms = {}
    for prop_name in set(p["name"] for p in [primary, secondary]):
        for r in frappe.get_all(
            "Home Room",
            filters={"property": prop_name},
            fields=["name", "room_name"],
        ):
            rooms[(prop_name, r["room_name"])] = r["name"]

    created = 0
    for idx, (
        item_name, category, brand, model, serial_number,
        purchase_date, purchase_price, estimated_value,
        condition, insured, room_label, notes,
    ) in enumerate(EXAMPLES):
        prop = assignments[idx]

        # Skip if item with same name + property already exists
        if frappe.db.exists("Home Item", {
            "item_name": item_name,
            "property": prop["name"],
        }):
            print(f"Skipping — {item_name} already exists on {prop['name']}")
            continue

        room = rooms.get((prop["name"], room_label)) if room_label else None

        doc = frappe.get_doc({
            "doctype": "Home Item",
            "item_type": "Possession",
            "household": prop["household"],
            "item_name": item_name,
            "property": prop["name"],
            "room": room,
            "category": category,
            "brand": brand,
            "model": model,
            "serial_number": serial_number,
            "purchase_date": purchase_date,
            "purchase_price": purchase_price,
            "estimated_value": estimated_value,
            "condition": condition,
            "insured": 1 if insured else 0,
            "notes": notes,
        })
        doc.insert(ignore_permissions=True)
        created += 1
        print(f"Created {doc.name} — {item_name} ({category}) on {prop['name']}")

    frappe.db.commit()
    print(f"\nDone — {created} possession items created.")
