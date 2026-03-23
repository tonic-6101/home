# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Seed script: creates 10 example appliance items for development/demo.

Usage (inside the Docker container):
    bench --site home.localhost execute home.seed_appliances.seed

Prerequisites: at least one Home Property must exist.
The script uses the first property it finds (or HP-0007 / HP-0004 if they exist).
"""

import frappe


EXAMPLES = [
    # (item_name, category, brand, model, serial_number, purchase_date, purchase_price, room_label, notes)  # noqa: E501
    (
        "Kühlschrank", "White Goods", "Liebherr", "CNsfd 5723",
        "LH-2023-44821", "2023-04-01", 899.00, "Kitchen",
        "Fridge-freezer combo, NoFrost. Bought at Saturn.",
    ),
    (
        "Waschmaschine", "White Goods", "Bosch", "WAX32M41",
        "BSH-2023-71055", "2023-06-15", 749.00, "Utility Room",
        "Front-loader, 9 kg capacity. i-DOS automatic dosing.",
    ),
    (
        "Geschirrspüler", "White Goods", "Miele", "G 7160 SCVi",
        "ML-2024-00392", "2024-01-10", 1299.00, "Kitchen",
        "Fully integrated 60 cm. AutoDos with PowerDisk.",
    ),
    (
        "Heizkessel", "Heating", "Viessmann", "Vitodens 200-W",
        "VS-2021-88340", "2021-11-15", 4200.00, None,
        "Gas condensing boiler, 26 kW. Annual service required for warranty.",
    ),
    (
        "Klimaanlage Wohnzimmer", "HVAC", "Daikin", "FTXM35R",
        "DK-2024-15602", "2024-03-20", 1850.00, "Living Room",
        "Split unit, 3.5 kW cooling. R-32 refrigerant.",
    ),
    (
        "Fernseher", "Electronics", "Samsung", "QE65S95D",
        "SM-2024-62148", "2024-11-25", 2199.00, "Living Room",
        "65-inch QD-OLED, 4K 144 Hz. Wall-mounted.",
    ),
    (
        "Backofen", "Kitchen", "Siemens", "HB674GBS1",
        "SI-2024-30771", "2024-05-01", 849.00, "Kitchen",
        "Built-in oven with activeClean pyrolysis.",
    ),
    (
        "Kaffeemaschine", "Kitchen", "De'Longhi", "Dinamica Plus ECAM370.95.T",
        "DL-2024-04519", "2024-08-10", 699.00, "Kitchen",
        "Fully automatic bean-to-cup. LatteCrema system.",
    ),
    (
        "Trockner", "White Goods", "Samsung", "DV90T6240LH",
        "SM-2023-41283", "2023-09-01", 649.00, "Utility Room",
        "Heat-pump dryer, 9 kg. AI Dry sensor.",
    ),
    (
        "Durchlauferhitzer", "Plumbing", "Stiebel Eltron", "DHB 21 ST",
        "SE-2020-77460", "2020-07-01", 329.00, "Bathroom",
        "Electronic instantaneous water heater, 21 kW.",
    ),
]


def seed():
    """Create 10 example appliance items on existing properties."""

    # Find properties to attach items to.
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

    # First 8 items go on primary property, last 2 on secondary
    assignments = [primary] * 8 + [secondary] * 2

    # Build a room lookup: room label → room name for each property
    rooms = {}
    for prop in set(p["name"] for p in [primary, secondary]):
        for r in frappe.get_all(
            "Home Room",
            filters={"property": prop},
            fields=["name", "room_name"],
        ):
            rooms[(prop, r["room_name"])] = r["name"]

    created = 0
    for idx, (
        item_name, category, brand, model, serial_number,
        purchase_date, purchase_price, room_label, notes,
    ) in enumerate(EXAMPLES):
        prop = assignments[idx]

        # Skip if an item with same name + property already exists
        if frappe.db.exists("Home Item", {
            "item_name": item_name,
            "property": prop["name"],
        }):
            print(f"Skipping — {item_name} already exists on {prop['name']}")
            continue

        room = rooms.get((prop["name"], room_label)) if room_label else None

        doc = frappe.get_doc({
            "doctype": "Home Item",
            "item_type": "Appliance",
            "household": prop["household"],
            "item_name": item_name,
            "property": prop["name"],
            "room": room,
            "category": category,
            "status": "Working",
            "brand": brand,
            "model": model,
            "serial_number": serial_number,
            "purchase_date": purchase_date,
            "purchase_price": purchase_price,
            "notes": notes,
        })
        doc.insert(ignore_permissions=True)
        created += 1
        print(f"Created {doc.name} — {item_name} ({brand} {model}) on {prop['name']}")

    frappe.db.commit()
    print(f"\nDone — {created} appliance items created.")
