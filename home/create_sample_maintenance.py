# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic
"""
Create 100 example Home Maintenance records for demo/testing.
Run: bench --site dock16.localhost execute home.create_sample_maintenance.run
"""
import random
from datetime import date, timedelta

import frappe

HOUSEHOLD = "HH-0020"
PROPERTY = "HP-0022"

# Contractors (will be used as free-text since Contact may not have these)
CONTRACTORS = [
    "Mueller Plumbing GmbH",
    "Schmidt Elektrotechnik",
    "Weber Heating & Cooling",
    "Fischer Roofing Co.",
    "Becker Painting",
    "Hoffmann Carpentry",
    "Schulz Garden Services",
    "Wagner Pest Control",
    "Koch General Repairs",
    "Bauer Home Inspections",
    "",  # no contractor (DIY)
    "",
    "",
]

# (title, category, maintenance_type, recurrence, room_name, item_name, cost_range, notes)
# room_name/item_name = None means no link
TASKS = [
    # Plumbing — 10 tasks
    ("Fix leaking kitchen faucet", "Plumbing", "One-off", None, "Kitchen", "Kitchen Faucet", (80, 250), "Dripping noticed under sink"),
    ("Replace toilet flush valve", "Plumbing", "One-off", None, "Bathroom", "Toilet", (50, 150), "Toilet running intermittently"),
    ("Annual water heater flush", "Plumbing", "Recurring", "Annual", "Bathroom", "Water Heater", (100, 200), "Drain sediment buildup to extend lifespan"),
    ("Unclog bathroom drain", "Plumbing", "One-off", None, "Bathroom", None, (60, 120), "Slow drainage in shower"),
    ("Check water softener salt level", "Plumbing", "Recurring", "Monthly", "Basement", "Water Softener", (0, 30), "Top up salt as needed"),
    ("Inspect sump pump", "Plumbing", "Recurring", "Quarterly", "Basement", "Sump Pump", (0, 50), "Test float switch and check valve"),
    ("Replace shower head seal", "Plumbing", "One-off", None, "En-Suite", "Rainfall Shower Head", (10, 30), "Minor leak at connection"),
    ("Winterize outdoor faucets", "Plumbing", "Recurring", "Annual", None, None, (0, 50), "Shut off and drain before first frost"),
    ("Fix bathtub drain stopper", "Plumbing", "One-off", None, "Bathroom", "Bathtub", (30, 80), "Stopper not sealing properly"),
    ("Replace washing machine hoses", "Plumbing", "One-off", None, "Laundry Room", "Washing Machine", (20, 60), "Preventive — hoses over 5 years old"),

    # Electrical — 8 tasks
    ("Replace smoke detector batteries", "Electrical", "Recurring", "Bi-annual", "Hallway", "Smoke Detector", (10, 25), "Test all detectors after replacement"),
    ("Fix flickering hallway light", "Electrical", "One-off", None, "Hallway", None, (40, 120), "Likely loose connection in switch"),
    ("Install additional outdoor outlet", "Electrical", "One-off", None, "Garden", None, (150, 400), "For garden lighting and power tools"),
    ("Annual electrical panel inspection", "Electrical", "Recurring", "Annual", "Basement", None, (100, 250), "Check breakers, look for signs of overheating"),
    ("Replace dimmer switch in living room", "Electrical", "One-off", None, "Living Room", None, (30, 80), "Upgrade to LED-compatible dimmer"),
    ("Fix UPS battery replacement", "Electrical", "One-off", None, "Home Office", "UPS Battery Backup", (60, 150), "Battery no longer holding charge"),
    ("Install motion sensor light (garage)", "Electrical", "One-off", None, "Garage", None, (50, 150), "Security and convenience"),
    ("Check GFCI outlets in wet areas", "Electrical", "Recurring", "Annual", "Kitchen", None, (0, 50), "Test and reset all GFCI outlets"),

    # HVAC & Heating — 12 tasks
    ("Annual boiler service", "HVAC & Heating", "Recurring", "Annual", "Basement", "Central Heating Boiler", (150, 350), "Mandatory annual inspection by certified tech"),
    ("Replace HVAC air filters", "HVAC & Heating", "Recurring", "Quarterly", None, None, (20, 60), "Use MERV 11 or higher filters"),
    ("Clean AC condenser coils", "HVAC & Heating", "Recurring", "Annual", "Living Room", "Air Conditioner (Living)", (80, 200), "Before summer season"),
    ("Bleed radiators", "HVAC & Heating", "Recurring", "Annual", None, None, (0, 20), "All radiators, start from top floor down"),
    ("Thermostat recalibration", "HVAC & Heating", "One-off", None, "Hallway", "Thermostat", (0, 50), "Temperature reading seems 2° off"),
    ("Replace air purifier filter", "HVAC & Heating", "Recurring", "Bi-annual", "Living Room", "Air Purifier", (30, 80), "Use genuine Dyson replacement filter"),
    ("Service dehumidifier", "HVAC & Heating", "Recurring", "Annual", "Basement", "Dehumidifier", (0, 40), "Clean filter, check drain hose, inspect coils"),
    ("Insulate hot water pipes", "HVAC & Heating", "One-off", None, "Basement", None, (50, 150), "Reduce heat loss and save energy"),
    ("Check towel radiator valve", "HVAC & Heating", "One-off", None, "Bathroom", "Towel Radiator", (20, 60), "Not heating up fully"),
    ("Clean range hood filters", "HVAC & Heating", "Recurring", "Quarterly", "Kitchen", "Range Hood", (0, 15), "Degrease metal filters in dishwasher"),
    ("Portable heater safety check", "HVAC & Heating", "Recurring", "Annual", "Home Office", "Portable Heater", (0, 20), "Check cord, plug, and tip-over switch"),
    ("Flush heating system", "HVAC & Heating", "One-off", None, "Basement", "Central Heating Boiler", (200, 500), "Power flush to remove sludge buildup"),

    # Painting & Decorating — 8 tasks
    ("Repaint kids room", "Painting & Decorating", "One-off", None, "Kids Room", None, (100, 300), "Walls scuffed — use washable paint this time"),
    ("Touch up hallway paint", "Painting & Decorating", "One-off", None, "Hallway", None, (30, 80), "Scuff marks at chair height"),
    ("Repaint exterior window frames", "Painting & Decorating", "One-off", None, None, "Double-Glazed Windows (set)", (300, 800), "Peeling on south-facing windows"),
    ("Stain and seal pergola", "Painting & Decorating", "Recurring", "Annual", "Garden", "Pergola", (100, 250), "Apply UV-resistant wood stain"),
    ("Repaint bathroom ceiling", "Painting & Decorating", "One-off", None, "Bathroom", None, (60, 150), "Use moisture-resistant paint"),
    ("Wallpaper accent wall (bedroom)", "Painting & Decorating", "One-off", None, "Master Bedroom", None, (150, 400), "Behind headboard wall"),
    ("Paint garden fence", "Painting & Decorating", "Recurring", "Annual", "Garden", "Garden Fence", (80, 200), "Weather protection coat"),
    ("Refinish front door", "Painting & Decorating", "One-off", None, "Hallway", "Front Door", (100, 250), "Sand, prime, and repaint"),

    # Carpentry — 6 tasks
    ("Fix squeaky stair treads", "Carpentry", "One-off", None, "Hallway", None, (50, 150), "3rd and 7th steps from bottom"),
    ("Adjust wardrobe door alignment", "Carpentry", "One-off", None, "Master Bedroom", "Wardrobe", (30, 80), "Sliding door catching on track"),
    ("Replace kitchen cabinet hinges", "Carpentry", "One-off", None, "Kitchen", "Kitchen Cabinets (set)", (40, 100), "Soft-close hinges wearing out"),
    ("Fix bathroom vanity drawer", "Carpentry", "One-off", None, "Bathroom", "Bathroom Vanity", (20, 60), "Drawer slides need replacement"),
    ("Install floating shelves (office)", "Carpentry", "One-off", None, "Home Office", None, (60, 180), "Above desk for books and supplies"),
    ("Repair bunk bed ladder", "Carpentry", "One-off", None, "Kids Room", "Bunk Bed", (30, 80), "Loose rung needs re-gluing"),

    # Roofing & Gutters — 8 tasks
    ("Clean gutters (spring)", "Roofing & Gutters", "Recurring", "Bi-annual", None, "Gutters & Downpipes", (80, 200), "Remove leaves and debris, check for damage"),
    ("Clean gutters (autumn)", "Roofing & Gutters", "Recurring", "Bi-annual", None, "Gutters & Downpipes", (80, 200), "Post leaf-fall cleanup"),
    ("Inspect roof tiles after storm", "Roofing & Gutters", "One-off", None, None, "Roof Tiles", (0, 100), "Visual inspection from ground + binoculars"),
    ("Replace cracked roof tiles", "Roofing & Gutters", "One-off", None, None, "Roof Tiles", (200, 600), "3 tiles cracked on west side"),
    ("Repair gutter downpipe joint", "Roofing & Gutters", "One-off", None, None, "Gutters & Downpipes", (40, 120), "Leaking at elbow joint near garage"),
    ("Inspect skylight seals", "Roofing & Gutters", "Recurring", "Annual", "Attic", "Skylight", (50, 150), "Check for condensation and seal integrity"),
    ("Moss removal from roof", "Roofing & Gutters", "One-off", None, None, "Roof Tiles", (200, 500), "North-facing slope has significant growth"),
    ("Install gutter guards", "Roofing & Gutters", "One-off", None, None, "Gutters & Downpipes", (300, 700), "Reduce frequency of gutter cleaning"),

    # Cleaning — 10 tasks
    ("Deep clean kitchen appliances", "Cleaning", "Recurring", "Quarterly", "Kitchen", None, (0, 50), "Oven, dishwasher, refrigerator coils"),
    ("Professional carpet cleaning", "Cleaning", "Recurring", "Annual", "Living Room", None, (150, 350), "Steam clean living room and bedrooms"),
    ("Clean dryer vent duct", "Cleaning", "Recurring", "Annual", "Laundry Room", "Dryer", (50, 120), "Fire prevention — remove lint buildup"),
    ("Power wash driveway", "Cleaning", "Recurring", "Annual", None, "Driveway Pavers", (80, 200), "Remove moss and stains"),
    ("Clean wine cooler condenser", "Cleaning", "Recurring", "Bi-annual", "Kitchen", "Wine Cooler", (0, 20), "Vacuum condenser coils at back"),
    ("Window cleaning (exterior)", "Cleaning", "Recurring", "Bi-annual", None, None, (100, 250), "All exterior windows including skylight"),
    ("Deep clean bathroom grout", "Cleaning", "One-off", None, "Bathroom", "Tile Floor (Bathroom)", (40, 100), "Re-seal grout after cleaning"),
    ("Clean and treat oak hardwood floor", "Cleaning", "Recurring", "Annual", "Living Room", "Oak Hardwood Floor (Living)", (80, 200), "Oil treatment to maintain finish"),
    ("Descale coffee machine", "Cleaning", "Recurring", "Monthly", "Kitchen", "Coffee Machine", (5, 15), "Use manufacturer-recommended descaler"),
    ("Clean refrigerator coils", "Cleaning", "Recurring", "Bi-annual", "Kitchen", "Refrigerator", (0, 20), "Pull out and vacuum underneath"),

    # Garden & Landscaping — 10 tasks
    ("Spring lawn aeration", "Garden & Landscaping", "Recurring", "Annual", "Garden", None, (50, 150), "Core aerate before fertilizing"),
    ("Autumn leaf cleanup", "Garden & Landscaping", "Recurring", "Annual", "Garden", None, (0, 80), "Mulch or bag fallen leaves"),
    ("Trim hedges", "Garden & Landscaping", "Recurring", "Quarterly", "Garden", None, (0, 60), "Keep height below fence line"),
    ("Sharpen and service lawnmower", "Garden & Landscaping", "Recurring", "Annual", "Garage", "Lawnmower", (30, 80), "Oil change, blade sharpening, spark plug"),
    ("Tree pruning (front yard)", "Garden & Landscaping", "One-off", None, "Garden", None, (200, 600), "Overhanging branches near roof"),
    ("Repair garden fence section", "Garden & Landscaping", "One-off", None, "Garden", "Garden Fence", (80, 250), "Storm damaged panel on east side"),
    ("Re-level patio pavers", "Garden & Landscaping", "One-off", None, "Garden", None, (100, 300), "Frost heave shifted several pavers"),
    ("Fertilize lawn (spring)", "Garden & Landscaping", "Recurring", "Annual", "Garden", None, (20, 60), "Apply slow-release fertilizer"),
    ("Winterize irrigation system", "Garden & Landscaping", "Recurring", "Annual", "Garden", None, (50, 120), "Blow out lines before frost"),
    ("Replace chainsaw chain", "Garden & Landscaping", "One-off", None, "Garage", "Chainsaw", (15, 40), "Chain dull after last season"),

    # Pest Control — 4 tasks
    ("Annual termite inspection", "Pest Control", "Recurring", "Annual", "Basement", None, (100, 250), "Certified inspector required"),
    ("Mouse traps in attic", "Pest Control", "One-off", None, "Attic", None, (20, 50), "Signs of rodent activity near insulation"),
    ("Wasp nest removal (eaves)", "Pest Control", "One-off", None, None, None, (60, 150), "Active nest above garage door"),
    ("Ant treatment (kitchen)", "Pest Control", "One-off", None, "Kitchen", None, (30, 80), "Trail along baseboard near dishwasher"),

    # Inspection — 8 tasks
    ("Annual home insurance inspection", "Inspection", "Recurring", "Annual", None, None, (0, 100), "Required by insurance provider"),
    ("Pre-winter property walkthrough", "Inspection", "Recurring", "Annual", None, None, (0, 0), "Check weatherstripping, caulking, exterior"),
    ("Check fire extinguisher expiry", "Inspection", "Recurring", "Annual", "Kitchen", None, (0, 30), "Replace if past expiry date"),
    ("Inspect French door seals", "Inspection", "Recurring", "Annual", "Living Room", "French Doors (Patio)", (0, 50), "Check for drafts and water intrusion"),
    ("Test all window locks", "Inspection", "Recurring", "Annual", None, "Double-Glazed Windows (set)", (0, 30), "Security check — lubricate mechanisms"),
    ("Inspect attic insulation", "Inspection", "One-off", None, "Attic", None, (0, 50), "Check for settling or moisture damage"),
    ("Foundation crack inspection", "Inspection", "One-off", None, "Basement", None, (100, 300), "Hairline crack appeared near corner"),
    ("Check garage door mechanism", "Inspection", "Recurring", "Annual", "Garage", None, (20, 60), "Lubricate tracks, test auto-reverse"),

    # General Repair — 10 tasks
    ("Fix dishwasher door latch", "General Repair", "One-off", None, "Kitchen", "Dishwasher", (30, 80), "Door not latching securely"),
    ("Replace dryer belt", "General Repair", "One-off", None, "Laundry Room", "Dryer", (40, 100), "Squeaking noise during operation"),
    ("Repair treadmill belt alignment", "General Repair", "One-off", None, "Basement", "Treadmill", (30, 80), "Belt drifting to one side"),
    ("Fix ice maker water line", "General Repair", "One-off", None, "Kitchen", "Ice Maker", (40, 120), "Reduced ice production"),
    ("Reattach kitchen tile", "General Repair", "One-off", None, "Kitchen", "Tile Floor (Kitchen)", (20, 60), "One tile loose near island"),
    ("Replace oven door seal", "General Repair", "One-off", None, "Kitchen", "Oven", (25, 60), "Heat escaping — gasket worn"),
    ("Fix sticking French door", "General Repair", "One-off", None, "Living Room", "French Doors (Patio)", (40, 120), "Wood swelling in humid weather"),
    ("Repair desk cable management", "General Repair", "One-off", None, "Home Office", "Office Desk", (15, 40), "Cable tray came loose"),
    ("Tighten dining chair joints", "General Repair", "One-off", None, "Dining Room", "Dining Chairs (set of 6)", (0, 30), "Two chairs wobbling"),
    ("Fix induction cooktop error", "General Repair", "One-off", None, "Kitchen", "Induction Cooktop", (80, 250), "E3 error code on right burner"),

    # Other — 6 tasks
    ("Update home inventory photos", "Other", "Recurring", "Annual", None, None, (0, 0), "Photograph all rooms for insurance records"),
    ("Organize garage storage", "Other", "One-off", None, "Garage", None, (50, 200), "Install wall-mounted tool racks"),
    ("Label electrical panel circuits", "Other", "One-off", None, "Basement", None, (0, 20), "Map and label all breakers"),
    ("Archive old manuals digitally", "Other", "One-off", None, "Home Office", None, (0, 0), "Scan and attach to item records"),
    ("Declutter attic storage", "Other", "One-off", None, "Attic", None, (0, 0), "Sort, donate, or dispose of unused items"),
    ("Emergency supply kit check", "Other", "Recurring", "Annual", None, None, (20, 80), "Check expiry dates, restock as needed"),
]


def _rand_date(start_year=2024, end_year=2026):
    start = date(start_year, 1, 1)
    end = date(end_year, 6, 30)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _rand_cost(cost_range):
    low, high = cost_range
    if low == 0 and high == 0:
        return 0
    return round(random.uniform(low, high), 2)


def run():
    random.seed(99)

    # Build lookup maps
    rooms = frappe.get_all(
        "Home Room",
        filters={"property": PROPERTY},
        fields=["name", "room_name"],
    )
    room_map = {r.room_name: r.name for r in rooms}

    items = frappe.get_all(
        "Home Item",
        filters={"property": PROPERTY},
        fields=["name", "item_name"],
        limit_page_length=0,
    )
    item_map = {i.item_name: i.name for i in items}

    # Check existing to avoid duplicates
    existing = set(
        r.title
        for r in frappe.get_all(
            "Home Maintenance",
            filters={"property": PROPERTY},
            fields=["title"],
            limit_page_length=0,
        )
    )

    created = 0
    skipped = 0

    for title, category, mtype, recurrence, room_name, item_name, cost_range, notes in TASKS:
        if title in existing:
            skipped += 1
            continue

        scheduled = _rand_date()
        # Determine status based on date
        today = date(2026, 3, 25)
        if scheduled < today - timedelta(days=30):
            status = random.choice(["Completed", "Completed", "Completed", "Cancelled"])
        elif scheduled < today:
            status = random.choice(["Completed", "In Progress", "Completed"])
        else:
            status = random.choice(["Scheduled", "Scheduled", "In Progress"])

        completed_date = None
        if status == "Completed":
            offset = random.randint(0, 7)
            completed_date = str(scheduled + timedelta(days=offset))

        cost = _rand_cost(cost_range) if status in ("Completed", "In Progress") else None

        room = room_map.get(room_name) if room_name else None
        item = item_map.get(item_name) if item_name else None

        contractor_name = random.choice(CONTRACTORS)

        doc = frappe.get_doc({
            "doctype": "Home Maintenance",
            "household": HOUSEHOLD,
            "property": PROPERTY,
            "title": title,
            "room": room,
            "item": item,
            "maintenance_type": mtype,
            "category": category,
            "status": status,
            "recurrence": recurrence if mtype == "Recurring" else None,
            "scheduled_date": str(scheduled),
            "completed_date": completed_date,
            "cost": cost,
            "notes": notes,
        })
        doc.insert(ignore_permissions=True)
        created += 1

    frappe.db.commit()
    print(f"\nDone! Created {created} maintenance tasks, skipped {skipped} duplicates.")
    print(f"Total maintenance for property: {frappe.db.count('Home Maintenance', {'property': PROPERTY})}")
