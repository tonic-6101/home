# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic
"""
Create 100 example Home Items with rooms for demo/testing.
Run: bench --site dock16.localhost execute home.create_sample_items.run
"""
import random
from datetime import date, timedelta

import frappe

HOUSEHOLD = "HH-0020"
PROPERTY = "HP-0022"

ROOMS = [
    ("Kitchen", "Kitchen"),
    ("Living Room", "Living Room"),
    ("Master Bedroom", "Bedroom"),
    ("Guest Bedroom", "Bedroom"),
    ("Kids Room", "Bedroom"),
    ("Bathroom", "Bathroom"),
    ("En-Suite", "Bathroom"),
    ("Home Office", "Other"),
    ("Garage", "Garage"),
    ("Laundry Room", "Other"),
    ("Basement", "Storage"),
    ("Attic", "Storage"),
    ("Garden", "Other"),
    ("Hallway", "Other"),
    ("Dining Room", "Other"),
]

# (item_name, item_type, category, brand, model, room_index, lifespan, price_range, material)
# room_index maps to ROOMS list above; None = no room
ITEMS = [
    # Kitchen Appliances
    ("Refrigerator", "Appliance", "White Goods", "Samsung", "RF28R7351SR", 0, 15, (800, 2500), None),
    ("Dishwasher", "Appliance", "White Goods", "Bosch", "SHPM88Z75N", 0, 12, (500, 1200), None),
    ("Oven", "Appliance", "Kitchen", "Miele", "H7464BP", 0, 15, (1200, 3500), None),
    ("Microwave", "Appliance", "Kitchen", "Panasonic", "NN-SN966S", 0, 10, (100, 400), None),
    ("Toaster", "Appliance", "Kitchen", "Breville", "BTA840XL", 0, 8, (50, 200), None),
    ("Coffee Machine", "Appliance", "Kitchen", "De'Longhi", "ECAM35075SI", 0, 8, (300, 1500), None),
    ("Stand Mixer", "Appliance", "Kitchen", "KitchenAid", "KSM150PS", 0, 20, (250, 500), None),
    ("Blender", "Appliance", "Kitchen", "Vitamix", "E310", 0, 10, (200, 500), None),
    ("Food Processor", "Appliance", "Kitchen", "Cuisinart", "DFP-14BCWN", 0, 12, (100, 300), None),
    ("Kettle", "Appliance", "Kitchen", "Fellow", "Stagg EKG", 0, 5, (50, 170), None),
    ("Induction Cooktop", "Appliance", "Kitchen", "Bosch", "NIT8069UC", 0, 15, (800, 2000), None),
    ("Range Hood", "Appliance", "Kitchen", "Zephyr", "AK7500BS", 0, 15, (400, 1200), None),
    ("Wine Cooler", "Appliance", "Kitchen", "EuroCave", "V-Prem-S", 0, 12, (500, 2000), None),
    ("Ice Maker", "Appliance", "Kitchen", "GE Profile", "Opal 2.0", 0, 8, (300, 600), None),
    # Laundry
    ("Washing Machine", "Appliance", "White Goods", "LG", "WM4500HBA", 9, 12, (600, 1500), None),
    ("Dryer", "Appliance", "White Goods", "LG", "DLEX4500B", 9, 12, (500, 1200), None),
    ("Iron", "Appliance", "White Goods", "Rowenta", "DW5280", 9, 8, (50, 150), None),
    ("Steam Press", "Appliance", "White Goods", "Singer", "ESP2", 9, 10, (100, 300), None),
    # HVAC
    ("Central Heating Boiler", "Appliance", "HVAC", "Viessmann", "Vitodens 200-W", 10, 20, (3000, 8000), None),
    ("Air Conditioner (Living)", "Appliance", "HVAC", "Daikin", "FTXS35K", 1, 15, (1500, 4000), None),
    ("Air Purifier", "Appliance", "HVAC", "Dyson", "TP07", 1, 8, (300, 700), None),
    ("Dehumidifier", "Appliance", "HVAC", "Frigidaire", "FFAD5033W1", 10, 10, (150, 400), None),
    ("Portable Heater", "Appliance", "Heating", "Dyson", "AM09", 7, 10, (200, 500), None),
    ("Thermostat", "Appliance", "HVAC", "Nest", "Learning 3rd Gen", 13, 10, (150, 250), None),
    # Electronics - Living Room
    ("TV 65\"", "Appliance", "Electronics", "LG", "OLED65C3", 1, 10, (1200, 2500), None),
    ("Soundbar", "Appliance", "Electronics", "Sonos", "Arc", 1, 10, (500, 900), None),
    ("Streaming Box", "Appliance", "Electronics", "Apple", "TV 4K", 1, 5, (100, 200), None),
    ("Game Console", "Appliance", "Electronics", "Sony", "PlayStation 5", 1, 8, (400, 500), None),
    ("Turntable", "Appliance", "Electronics", "Audio-Technica", "AT-LP120X", 1, 15, (200, 400), None),
    ("Amplifier", "Appliance", "Electronics", "Marantz", "PM7000N", 1, 20, (500, 1200), None),
    # Electronics - Office
    ("Desktop Computer", "Appliance", "Electronics", "Apple", "Mac Studio M2 Ultra", 7, 7, (2000, 4000), None),
    ("Monitor 27\"", "Appliance", "Electronics", "Dell", "U2723QE", 7, 8, (400, 700), None),
    ("Laser Printer", "Appliance", "Electronics", "Brother", "HL-L2395DW", 7, 8, (150, 300), None),
    ("UPS Battery Backup", "Appliance", "Electronics", "APC", "BR1500MS2", 7, 5, (150, 300), None),
    ("WiFi Router", "Appliance", "Electronics", "Ubiquiti", "Dream Machine Pro", 7, 7, (300, 500), None),
    ("NAS Storage", "Appliance", "Electronics", "Synology", "DS923+", 7, 8, (500, 1000), None),
    # Plumbing
    ("Water Heater", "Appliance", "Plumbing", "Stiebel Eltron", "Tempra 24 Plus", 5, 15, (500, 1500), None),
    ("Sump Pump", "Appliance", "Plumbing", "Zoeller", "M53", 10, 10, (150, 400), None),
    ("Water Softener", "Appliance", "Plumbing", "Grünbeck", "softliQ SD18", 10, 15, (800, 2000), None),
    # Garden / Outdoor
    ("Lawnmower", "Appliance", "Garden & Landscape", "Honda", "HRX217VKA", 12, 10, (400, 800), None),
    ("Hedge Trimmer", "Appliance", "Garden & Landscape", "Stihl", "HSA 56", 12, 8, (150, 350), None),
    ("Pressure Washer", "Appliance", "Garden & Landscape", "Kärcher", "K5 Premium", 8, 10, (250, 500), None),
    ("Leaf Blower", "Appliance", "Garden & Landscape", "EGO Power+", "LB6504", 8, 8, (200, 400), None),
    ("Chainsaw", "Appliance", "Tools & Equipment", "Husqvarna", "440e II", 8, 12, (300, 600), None),
    # Tools
    ("Drill/Driver Set", "Appliance", "Tools & Equipment", "Makita", "XFD131", 8, 15, (100, 300), None),
    ("Table Saw", "Appliance", "Tools & Equipment", "DeWalt", "DWE7491RS", 8, 20, (400, 700), None),
    ("Compressor", "Appliance", "Tools & Equipment", "Makita", "MAC2400", 8, 15, (250, 500), None),
    # Furniture - Living Room
    ("Sofa (3-seater)", "Possession", "Furniture", "Muuto", "Outline", 1, None, (2000, 5000), None),
    ("Coffee Table", "Possession", "Furniture", "HAY", "Slit Table", 1, None, (200, 600), None),
    ("Bookshelf", "Possession", "Furniture", "USM", "Haller", 1, None, (800, 3000), None),
    ("TV Console", "Possession", "Furniture", "BoConcept", "Lugano", 1, None, (500, 1500), None),
    ("Floor Lamp", "Possession", "Furniture", "Flos", "Arco", 1, None, (300, 2500), None),
    ("Rug (Living Room)", "Possession", "Furniture", "Hay", "Raw Rug No.2", 1, None, (400, 1500), None),
    # Furniture - Dining
    ("Dining Table", "Possession", "Furniture", "Vitra", "EM Table", 14, None, (1500, 4000), None),
    ("Dining Chairs (set of 6)", "Possession", "Furniture", "HAY", "AAC 22", 14, None, (600, 1800), None),
    ("Sideboard", "Possession", "Furniture", "Muuto", "Stacked", 14, None, (800, 2500), None),
    # Furniture - Bedroom
    ("Bed Frame (King)", "Possession", "Furniture", "Hästens", "Superia", 2, None, (1500, 5000), None),
    ("Mattress (King)", "Possession", "Furniture", "Emma", "Original", 2, None, (500, 1500), None),
    ("Wardrobe", "Possession", "Furniture", "IKEA", "PAX System", 2, None, (400, 1200), None),
    ("Nightstand (pair)", "Possession", "Furniture", "Normann Copenhagen", "Block Table", 2, None, (200, 600), None),
    ("Dresser", "Possession", "Furniture", "Ethnicraft", "Madra", 2, None, (800, 2000), None),
    ("Guest Bed (Double)", "Possession", "Furniture", "Muji", "Oak Bed Frame", 3, None, (500, 1200), None),
    ("Bunk Bed", "Possession", "Furniture", "Oliver Furniture", "Wood", 4, None, (800, 2000), None),
    # Furniture - Office
    ("Office Desk", "Possession", "Furniture", "Fully", "Jarvis Standing Desk", 7, None, (500, 1200), None),
    ("Office Chair", "Possession", "Furniture", "Herman Miller", "Aeron", 7, None, (800, 1800), None),
    ("Filing Cabinet", "Possession", "Furniture", "Vitra", "Cab", 7, None, (200, 600), None),
    # Jewelry & Watches
    ("Wristwatch", "Possession", "Jewelry & Watches", "Nomos", "Tangente 38", 2, None, (1500, 3000), None),
    ("Pearl Necklace", "Possession", "Jewelry & Watches", None, None, 2, None, (500, 2000), None),
    ("Wedding Rings (pair)", "Possession", "Jewelry & Watches", None, None, 2, None, (1000, 5000), None),
    # Art & Collectibles
    ("Oil Painting (landscape)", "Possession", "Art & Collectibles", None, None, 1, None, (300, 2000), None),
    ("Vinyl Record Collection", "Possession", "Art & Collectibles", None, None, 1, None, (500, 3000), None),
    ("Ceramic Vase", "Possession", "Art & Collectibles", "Heath Ceramics", None, 14, None, (100, 500), None),
    # Musical Instruments
    ("Acoustic Guitar", "Possession", "Musical Instruments", "Martin", "D-28", 1, None, (1500, 3500), None),
    ("Digital Piano", "Possession", "Musical Instruments", "Yamaha", "CLP-785", 1, None, (2000, 4000), None),
    # Sports Equipment
    ("Road Bicycle", "Possession", "Sports Equipment", "Canyon", "Endurace CF 7", 8, None, (1500, 3000), None),
    ("Ski Set (2 pairs)", "Possession", "Sports Equipment", "Völkl", "Deacon 84", 11, None, (800, 2000), None),
    ("Treadmill", "Appliance", "Sports Equipment", "NordicTrack", "Commercial 1750", 10, 10, (1000, 2500), None),
    ("Kayak", "Possession", "Sports Equipment", "Prijon", "Poseidon", 8, None, (600, 1500), None),
    # Fixtures - Kitchen
    ("Kitchen Faucet", "Fixture", "Fixtures & Fittings", "Hansgrohe", "Talis M54", 0, None, (200, 600), "Chrome"),
    ("Granite Countertop", "Fixture", "Fixtures & Fittings", None, None, 0, None, (2000, 8000), "Granite"),
    ("Kitchen Cabinets (set)", "Fixture", "Fixtures & Fittings", "Nolte", "Artwood", 0, None, (5000, 15000), "Oak/MDF"),
    # Fixtures - Bathroom
    ("Bathroom Vanity", "Fixture", "Fixtures & Fittings", "Duravit", "L-Cube", 5, None, (500, 2000), "Ceramic/Wood"),
    ("Bathtub", "Fixture", "Fixtures & Fittings", "Kaldewei", "Puro Duo", 5, None, (800, 3000), "Steel Enamel"),
    ("Rainfall Shower Head", "Fixture", "Fixtures & Fittings", "Hansgrohe", "Raindance S", 6, None, (200, 800), "Chrome"),
    ("Towel Radiator", "Fixture", "Heating", "Zehnder", "Metropolitan Spa", 5, None, (300, 900), "Steel"),
    ("Toilet", "Fixture", "Fixtures & Fittings", "Duravit", "Starck 3", 5, None, (300, 800), "Ceramic"),
    # Fixtures - Doors & Windows
    ("Front Door", "Fixture", "Doors & Windows", "Hörmann", "ThermoSafe", 13, None, (1500, 5000), "Aluminium"),
    ("French Doors (Patio)", "Fixture", "Doors & Windows", "Internorm", "HF 410", 1, None, (2000, 6000), "Wood/Aluminium"),
    ("Skylight", "Fixture", "Doors & Windows", "Velux", "GGU CK04", 11, None, (400, 1200), "Pine/Aluminium"),
    ("Double-Glazed Windows (set)", "Fixture", "Doors & Windows", "Internorm", "KF 520", None, None, (5000, 15000), "PVC"),
    # Fixtures - Walls & Floors
    ("Oak Hardwood Floor (Living)", "Fixture", "Walls & Floors", None, None, 1, None, (3000, 8000), "Oak"),
    ("Tile Floor (Bathroom)", "Fixture", "Walls & Floors", "Villeroy & Boch", "Astoria", 5, None, (1000, 3000), "Porcelain"),
    ("Tile Floor (Kitchen)", "Fixture", "Walls & Floors", "Marazzi", "Allmarble", 0, None, (1500, 4000), "Porcelain"),
    # Fixtures - Roof & Structure
    ("Roof Tiles", "Fixture", "Roof & Structure", "Braas", "Tegalit", None, None, (5000, 15000), "Concrete"),
    ("Gutters & Downpipes", "Fixture", "Roof & Structure", "Lindab", "Rainline", None, None, (800, 2500), "Steel"),
    # Fixtures - Exterior
    ("Garden Fence", "Fixture", "Exterior", None, None, 12, None, (1000, 4000), "Wood"),
    ("Driveway Pavers", "Fixture", "Exterior", None, None, None, None, (2000, 8000), "Concrete Block"),
    ("Pergola", "Fixture", "Exterior", None, None, 12, None, (1500, 5000), "Douglas Fir"),
    # Clothing
    ("Winter Coat Collection", "Possession", "Clothing & Accessories", None, None, 13, None, (300, 1500), None),
    # Smoke detector
    ("Smoke Detector", "Appliance", "Fixtures & Fittings", "Nest", "Protect 2nd Gen", 13, 10, (80, 130), None),
]


def _rand_date(start_year=2018, end_year=2025):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _rand_serial():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(chars) for _ in range(12))


def _rand_price(price_range):
    low, high = price_range
    return round(random.uniform(low, high), 2)


def run():
    random.seed(42)

    # Check existing rooms
    existing_rooms = frappe.get_all(
        "Home Room",
        filters={"property": PROPERTY},
        fields=["name", "room_name"],
    )
    room_map = {r.room_name: r.name for r in existing_rooms}

    # Create rooms if needed
    for room_name, room_type in ROOMS:
        if room_name not in room_map:
            doc = frappe.get_doc({
                "doctype": "Home Room",
                "household": HOUSEHOLD,
                "property": PROPERTY,
                "room_name": room_name,
                "room_type": room_type,
            })
            doc.insert(ignore_permissions=True)
            room_map[room_name] = doc.name
            print(f"  Created room: {room_name} ({doc.name})")

    frappe.db.commit()

    # Resolve room names to IDs
    room_ids = [room_map[ROOMS[i][0]] for i in range(len(ROOMS))]

    # Check existing items to avoid duplicates
    existing = set(
        r.item_name
        for r in frappe.get_all("Home Item", filters={"property": PROPERTY}, fields=["item_name"])
    )

    created = 0
    skipped = 0
    statuses = ["Working", "Working", "Working", "Working", "Needs Repair"]  # 80% working
    conditions = ["New", "Excellent", "Good", "Good", "Fair"]

    for item_name, item_type, category, brand, model, room_idx, lifespan, price_range, material in ITEMS:
        if item_name in existing:
            skipped += 1
            continue

        room = room_ids[room_idx] if room_idx is not None else None
        purchase_date = _rand_date()
        purchase_price = _rand_price(price_range)
        estimated_value = round(purchase_price * random.uniform(0.3, 0.9), 2)

        doc_data = {
            "doctype": "Home Item",
            "item_name": item_name,
            "item_type": item_type,
            "property": PROPERTY,
            "household": HOUSEHOLD,
            "room": room,
            "category": category,
            "brand": brand or "",
            "model": model or "",
            "serial_number": _rand_serial() if item_type == "Appliance" else "",
            "purchase_date": str(purchase_date),
            "purchase_price": purchase_price,
            "estimated_value": estimated_value,
            "insured": 1 if estimated_value > 1500 else 0,
        }

        if item_type == "Appliance":
            doc_data["status"] = random.choice(statuses)
            if lifespan:
                doc_data["expected_lifespan_years"] = lifespan

        if item_type == "Possession":
            doc_data["condition"] = random.choice(conditions)

        if item_type == "Fixture":
            doc_data["installed_date"] = str(_rand_date(2015, 2024))
            if material:
                doc_data["material"] = material

        doc = frappe.get_doc(doc_data)
        doc.insert(ignore_permissions=True)
        created += 1

    frappe.db.commit()
    print(f"\nDone! Created {created} items, skipped {skipped} duplicates.")
    print(f"Total items for property: {frappe.db.count('Home Item', {'property': PROPERTY})}")
