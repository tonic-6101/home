# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic
"""
Download 100 free Pexels photos and attach them to Home Items.
All photos are from Pexels (pexels.com) — free to use, no attribution required.
Run: bench --site dock16.localhost execute home.create_sample_photos.run
"""
import os
import time
import urllib.request
import urllib.error

import frappe

PROPERTY = "HP-0022"

# Pexels photo ID mapping: item_name → pexels_photo_id
# All photos are free under the Pexels license (https://www.pexels.com/license/)
PHOTO_MAP = {
    # Kitchen Appliances
    "Refrigerator": 8583864,
    "Dishwasher": 213162,
    "Oven": 7525215,
    "Microwave": 9462228,
    "Toaster": 5825716,
    "Coffee Machine": 2115210,
    "Stand Mixer": 14495889,
    "Blender": 7545855,
    "Food Processor": 4119836,
    "Kettle": 6255,
    "Induction Cooktop": 7168075,
    "Range Hood": 3992205,
    "Wine Cooler": 2079698,
    "Ice Maker": 4058699,
    # Laundry
    "Washing Machine": 7614539,
    "Dryer": 19846385,
    "Iron": 7282795,
    "Steam Press": 5591840,
    # HVAC & Heating
    "Central Heating Boiler": 11701114,
    "Air Conditioner (Living)": 6316067,
    "Air Purifier": 7166926,
    "Dehumidifier": 6283974,
    "Portable Heater": 5824522,
    "Thermostat": 7018822,
    # Electronics - Living Room
    "TV 65\"": 5813746,
    "Soundbar": 6316067,
    "Streaming Box": 7166926,
    "Game Console": 4219883,
    "Turntable": 908965,
    "Amplifier": 6862587,
    # Electronics - Office
    "Desktop Computer": 7899239,
    "Monitor 27\"": 15372903,
    "Laser Printer": 1714341,
    "UPS Battery Backup": 3610131,
    "WiFi Router": 20694726,
    "NAS Storage": 13162096,
    # Plumbing
    "Water Heater": 19776970,
    "Sump Pump": 1909791,
    "Water Softener": 17069809,
    # Garden / Outdoor
    "Lawnmower": 4162011,
    "Hedge Trimmer": 9229821,
    "Pressure Washer": 11364122,
    "Leaf Blower": 6728919,
    "Chainsaw": 9754817,
    # Tools
    "Drill/Driver Set": 9754817,
    "Table Saw": 17850,
    "Compressor": 9754817,
    # Furniture - Living Room
    "Sofa (3-seater)": 6316067,
    "Coffee Table": 7166926,
    "Bookshelf": 6862587,
    "TV Console": 5813746,
    "Floor Lamp": 6835179,
    "Rug (Living Room)": 6835178,
    # Furniture - Dining
    "Dining Table": 3773579,
    "Dining Chairs (set of 6)": 3968056,
    "Sideboard": 271647,
    # Furniture - Bedroom
    "Bed Frame (King)": 2029694,
    "Mattress (King)": 279746,
    "Wardrobe": 5824522,
    "Nightstand (pair)": 12277956,
    "Dresser": 376531,
    "Guest Bed (Double)": 279746,
    "Bunk Bed": 12277956,
    # Furniture - Office
    "Office Desk": 7899239,
    "Office Chair": 15372903,
    "Filing Cabinet": 1714341,
    # Jewelry & Watches
    "Wristwatch": 125779,
    "Pearl Necklace": 20858959,
    "Wedding Rings (pair)": 6691131,
    # Art & Collectibles
    "Oil Painting (landscape)": 1070527,
    "Vinyl Record Collection": 908965,
    "Ceramic Vase": 6732658,
    # Musical Instruments
    "Acoustic Guitar": 1010519,
    "Digital Piano": 5934,
    # Sports Equipment
    "Road Bicycle": 38296,
    "Ski Set (2 pairs)": 101666,
    "Treadmill": 1954524,
    "Kayak": 1088607,
    # Fixtures - Kitchen
    "Kitchen Faucet": 19991824,
    "Granite Countertop": 7545855,
    "Kitchen Cabinets (set)": 4119836,
    # Fixtures - Bathroom
    "Bathroom Vanity": 19776970,
    "Bathtub": 6283974,
    "Rainfall Shower Head": 7018822,
    "Towel Radiator": 11701114,
    "Toilet": 1909791,
    # Fixtures - Doors & Windows
    "Front Door": 8455428,
    "French Doors (Patio)": 19085454,
    "Skylight": 11613798,
    "Double-Glazed Windows (set)": 6835178,
    # Fixtures - Walls & Floors
    "Oak Hardwood Floor (Living)": 15066939,
    "Tile Floor (Bathroom)": 17069809,
    "Tile Floor (Kitchen)": 7533891,
    # Fixtures - Roof & Structure
    "Roof Tiles": 5668698,
    "Gutters & Downpipes": 15562216,
    # Fixtures - Exterior
    "Garden Fence": 5126304,
    "Driveway Pavers": 1860527,
    "Pergola": 5126304,
    # Clothing
    "Winter Coat Collection": 759678,
    # Safety
    "Smoke Detector": 759678,
}


def _pexels_url(photo_id):
    """Construct direct Pexels image URL (600px wide)."""
    return (
        f"https://images.pexels.com/photos/{photo_id}/"
        f"pexels-photo-{photo_id}.jpeg"
        f"?auto=compress&cs=tinysrgb&w=600"
    )


def _download(url, dest_path, retries=2):
    """Download a URL to a local file path with retries."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
            return True
        except (urllib.error.URLError, OSError) as e:
            if attempt < retries:
                time.sleep(1)
            else:
                print(f"  FAILED to download {url}: {e}")
                return False
    return False


def run():
    site = frappe.local.site
    files_dir = frappe.get_site_path("public", "files")
    os.makedirs(files_dir, exist_ok=True)

    # Get all items for this property
    items = frappe.get_all(
        "Home Item",
        filters={"property": PROPERTY},
        fields=["name", "item_name", "photo"],
        limit_page_length=0,
    )
    item_map = {i.item_name: i for i in items}

    downloaded = 0
    skipped = 0
    failed = 0

    for item_name, photo_id in PHOTO_MAP.items():
        item = item_map.get(item_name)
        if not item:
            print(f"  SKIP (not found): {item_name}")
            skipped += 1
            continue

        if item.photo:
            print(f"  SKIP (has photo): {item_name}")
            skipped += 1
            continue

        # Build filename
        safe_name = item_name.lower().replace(" ", "-").replace("/", "-")
        safe_name = safe_name.replace('"', "").replace("(", "").replace(")", "")
        safe_name = safe_name.replace("'", "")
        filename = f"home-item-{safe_name}-{photo_id}.jpg"
        file_path = os.path.join(files_dir, filename)
        file_url = f"/files/{filename}"

        # Download if not already on disk
        if not os.path.exists(file_path):
            url = _pexels_url(photo_id)
            print(f"  Downloading: {item_name} ← pexels:{photo_id}")
            ok = _download(url, file_path)
            if not ok:
                failed += 1
                continue
            # Small delay to be polite to Pexels
            time.sleep(0.3)
        else:
            print(f"  On disk: {filename}")

        # Create Frappe File doc if not exists
        existing_file = frappe.db.exists("File", {"file_url": file_url})
        if not existing_file:
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": filename,
                "file_url": file_url,
                "is_private": 0,
                "attached_to_doctype": "Home Item",
                "attached_to_name": item.name,
                "attached_to_field": "photo",
            })
            file_doc.insert(ignore_permissions=True)

        # Update the item's photo field
        frappe.db.set_value("Home Item", item.name, "photo", file_url)
        downloaded += 1

    frappe.db.commit()
    print(f"\nDone! Attached {downloaded} photos, skipped {skipped}, failed {failed}.")
    total_with_photo = frappe.db.count("Home Item", {"property": PROPERTY, "photo": ["!=", ""]})
    print(f"Items with photos: {total_with_photo} / {len(items)}")
