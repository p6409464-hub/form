"""
Crop Storage and Shelf-Life Recommendation Service
Provides scientific post-harvest handling rules, temperature/humidity requirements,
shelf-life calculation, and verified cold storage/warehouse directory for Tamil Nadu.
"""

from datetime import date, datetime

STORAGE_DATABASE = {
    "Tomato": {
        "tamil_name": "தக்காளி",
        "ambient_days": 6,
        "ambient_temp": "20°C - 25°C",
        "ambient_rh": "85% - 90%",
        "cold_days": 21,
        "cold_temp": "10°C - 12°C",
        "cold_rh": "90% - 95%",
        "chilling_injury_threshold": "< 10°C",
        "curing_needed": False,
        "ethylene_sensitive": True,
        "key_practices": [
            "Store pink/breaker stage tomatoes to extend market window.",
            "Never store below 10°C to prevent chilling injury and mealy texture.",
            "Keep stem/calyx intact to prevent bacterial soft rot.",
            "Stack plastic crates max 3 layers to avoid pressure bruising."
        ]
    },
    "Onion": {
        "tamil_name": "வெங்காயம்",
        "ambient_days": 75,
        "ambient_temp": "25°C - 30°C",
        "ambient_rh": "65% - 70%",
        "cold_days": 180,
        "cold_temp": "0°C - 2°C",
        "cold_rh": "65% - 70%",
        "chilling_injury_threshold": "None (freezing point -1°C)",
        "curing_needed": True,
        "ethylene_sensitive": False,
        "key_practices": [
            "Field curing: Sun dry with foliage for 3 to 5 days until neck is fully paper-dry.",
            "Store in well-ventilated slatted wooden or bamboo racks (Pattarai) with bottom airflow.",
            "Avoid high humidity (>75% RH) which induces sprouting and black mould (Aspergillus).",
            "Sort regularly and remove rotting or thick-neck bulbs."
        ]
    },
    "Turmeric": {
        "tamil_name": "மஞ்சள்",
        "ambient_days": 540,
        "ambient_temp": "20°C - 30°C",
        "ambient_rh": "60% - 65%",
        "cold_days": 720,
        "cold_temp": "12°C - 15°C",
        "cold_rh": "60% - 65%",
        "chilling_injury_threshold": "None",
        "curing_needed": True,
        "ethylene_sensitive": False,
        "key_practices": [
            "Boil rhizomes in copper/GI pans until soft (approx. 45-60 min).",
            "Sun dry on clean tarpaulins for 10-15 days until moisture drops below 10%.",
            "Mechanical polishing removes outer dull skin and improves shine and curcumin retention.",
            "Pack in moisture-proof gunny bags on wooden pallets in pest-controlled godowns."
        ]
    },
    "Coconut": {
        "tamil_name": "தேங்காய்",
        "ambient_days": 45,
        "ambient_temp": "25°C - 30°C",
        "ambient_rh": "70% - 75%",
        "cold_days": 90,
        "cold_temp": "12°C - 14°C",
        "cold_rh": "80% - 85%",
        "chilling_injury_threshold": "< 8°C",
        "curing_needed": False,
        "ethylene_sensitive": False,
        "key_practices": [
            "Store mature nuts with intact husk in shaded, airy sheds.",
            "For milling copra: Dry cups to < 6% moisture to prevent Aspergillus aflatoxin development.",
            "Never store fresh nuts on bare wet ground."
        ]
    },
    "Banana": {
        "tamil_name": "வாழை",
        "ambient_days": 7,
        "ambient_temp": "20°C - 26°C",
        "ambient_rh": "85% - 90%",
        "cold_days": 24,
        "cold_temp": "13°C - 14°C",
        "cold_rh": "90% - 95%",
        "chilling_injury_threshold": "< 12°C",
        "curing_needed": False,
        "ethylene_sensitive": True,
        "key_practices": [
            "De-hand bunches and wash in alum/citric water to remove latex stains.",
            "Store green mature stage in cold rooms with ethylene scrubbing.",
            "Ripen with ethylene gas (100 ppm) in controlled ripening chambers, not carbide."
        ]
    },
    "Potato": {
        "tamil_name": "உருளைக்கிழங்கு",
        "ambient_days": 25,
        "ambient_temp": "20°C - 24°C",
        "ambient_rh": "80% - 85%",
        "cold_days": 210,
        "cold_temp": "8°C - 10°C",
        "cold_rh": "90% - 95%",
        "chilling_injury_threshold": "< 4°C (converts starch to sugar)",
        "curing_needed": True,
        "ethylene_sensitive": True,
        "key_practices": [
            "Store in complete darkness to prevent solanine greening.",
            "Cure skin for 10 days at 15°C with high humidity before long-term storage.",
            "Keep away from onions as onions release ethylene which causes potato sprouting."
        ]
    },
    "Green Chilli": {
        "tamil_name": "பச்சை மிளகாய்",
        "ambient_days": 5,
        "ambient_temp": "22°C - 26°C",
        "ambient_rh": "80% - 85%",
        "cold_days": 18,
        "cold_temp": "8°C - 10°C",
        "cold_rh": "90% - 95%",
        "chilling_injury_threshold": "< 7°C",
        "curing_needed": False,
        "ethylene_sensitive": True,
        "key_practices": [
            "Sort out broken/wet stems to prevent anthracnose rot.",
            "Pack in ventilated CFB boxes with perforated liners."
        ]
    }
}

COLD_STORAGE_DIRECTORY = [
    {
        "name": "Pollachi Regulated Market Committee Cold Storage",
        "district": "Coimbatore",
        "location": "Market Road, Pollachi",
        "capacity_mt": 500,
        "suitable_for": "Coconut, Vegetables, Fruits",
        "rate_per_bag": "₹15 - ₹20 / month",
        "contact_phone": "+91 4259 223450",
        "ownership": "Govt of Tamil Nadu (Agri Marketing Dept)"
    },
    {
        "name": "Erode Turmeric Special Cold Storage (TNWC)",
        "district": "Erode",
        "location": "Perundurai Road, Erode",
        "capacity_mt": 5000,
        "suitable_for": "Turmeric, Spices, Grains",
        "rate_per_bag": "₹25 / quintal / month",
        "contact_phone": "+91 424 2251833",
        "ownership": "Tamil Nadu Warehousing Corporation"
    },
    {
        "name": "Palladam APMC Modern Onion Godown",
        "district": "Tiruppur",
        "location": "Dharapuram Road, Palladam",
        "capacity_mt": 1000,
        "suitable_for": "Small Onion / Shallots, Maize",
        "rate_per_bag": "₹12 / bag / month",
        "contact_phone": "+91 4255 252110",
        "ownership": "Regulated Market Committee, Tiruppur"
    },
    {
        "name": "Sathyamangalam Banana Ripening & Cold Storage",
        "district": "Erode",
        "location": "Athani Road, Sathyamangalam",
        "capacity_mt": 300,
        "suitable_for": "Banana, Fruits, Vegetables",
        "rate_per_bag": "₹18 / crate / month",
        "contact_phone": "+91 4295 220550",
        "ownership": "Cooperative Marketing Society"
    },
    {
        "name": "Udumalpet Regulated Cold Storage Yard",
        "district": "Tiruppur",
        "location": "Dharapuram Main Road, Udumalpet",
        "capacity_mt": 800,
        "suitable_for": "Coconut, Tomato, Onion",
        "rate_per_bag": "₹16 / bag / month",
        "contact_phone": "+91 4252 224320",
        "ownership": "Tamil Nadu Agricultural Marketing Board"
    }
]

def calculate_shelf_life(crop_name, harvest_date_str, storage_type="ambient"):
    """Calculates remaining safe shelf life days and alerts."""
    crop_info = STORAGE_DATABASE.get(crop_name, STORAGE_DATABASE["Tomato"])
    
    try:
        harvest_date = datetime.strptime(harvest_date_str, "%Y-%m-%d").date()
    except Exception:
        harvest_date = date.today()

    days_since_harvest = (date.today() - harvest_date).days
    total_life = crop_info["cold_days"] if storage_type == "cold" else crop_info["ambient_days"]
    remaining_days = max(0, total_life - days_since_harvest)
    pct_used = min(100.0, round((days_since_harvest / total_life) * 100, 1))

    if remaining_days <= 1:
        status = "CRITICAL_SPOILAGE_RISK"
        badge = "🔴 Sell / Process Immediately"
    elif remaining_days <= 4:
        status = "NEARING_EXPIRY"
        badge = "🟡 Moderate Life (Prioritize Sale)"
    else:
        status = "FRESH_PRIME"
        badge = "🟢 Prime Condition"

    return {
        "crop_name": crop_name,
        "tamil_name": crop_info["tamil_name"],
        "storage_type": storage_type,
        "harvest_date": str(harvest_date),
        "days_since_harvest": days_since_harvest,
        "total_shelf_life_days": total_life,
        "remaining_days": remaining_days,
        "life_consumed_pct": pct_used,
        "status": status,
        "status_badge": badge,
        "optimal_temperature": crop_info["cold_temp"] if storage_type == "cold" else crop_info["ambient_temp"],
        "optimal_humidity": crop_info["cold_rh"] if storage_type == "cold" else crop_info["ambient_rh"],
        "chilling_injury_threshold": crop_info["chilling_injury_threshold"],
        "key_practices": crop_info["key_practices"]
    }
