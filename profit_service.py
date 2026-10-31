"""
Profit Calculator and Best Market Recommendation Engine
Handles:
- Quintal to kg conversions
- Selling value calculations
- Distance estimation (Haversine formula + road multiplier) between Farmer Location & Mandis
- Dynamic transportation and other expense calculations
- Market-by-market comparison across Coimbatore, Tiruppur, and Erode
- Best market recommendation with net profit optimization
"""

import math
from datetime import date
from db import query_db, execute_db

# Coordinates lookup for common farmer locations across the Kongu belt
LOCATION_COORDINATES = {
    # Coimbatore
    "pollachi": (10.6585, 77.0084),
    "annur": (11.2333, 77.1000),
    "sulur": (11.0247, 77.1264),
    "kinathukkadavu": (10.8178, 77.0210),
    "coimbatore": (11.0168, 76.9558),
    "mettupalayam": (11.3000, 76.9400),
    "valparai": (10.3244, 76.9558),
    "thondamuthur": (10.9950, 76.8320),

    # Tiruppur
    "udumalpet": (10.5849, 77.2476),
    "dharapuram": (10.7303, 77.5255),
    "palladam": (10.9996, 77.2885),
    "kangayam": (11.0055, 77.5583),
    "tiruppur": (11.1085, 77.3411),
    "avanshi": (11.1928, 77.2685),
    "madathukulam": (10.5400, 77.3800),

    # Erode
    "erode": (11.3410, 77.7172),
    "gobichettipalayam": (11.4552, 77.4332),
    "perundurai": (11.2758, 77.5831),
    "bhavani": (11.4503, 77.6826),
    "sathyamangalam": (11.5034, 77.2427),
    "anthiyur": (11.5800, 77.6000),
    "kodumudi": (11.0778, 77.8861),
    "modakkurichi": (11.2167, 77.7667)
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two points in km,
    with a 1.25 road-curvature factor for Kongu agricultural roads.
    """
    R = 6371.0  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    straight_line_km = R * c
    
    # Realistic road distance (1.25 multiplier)
    road_km = round(max(5.0, straight_line_km * 1.25), 1)
    return road_km

def resolve_farmer_coordinates(location_str, district_fallback=None):
    """Finds coordinates for user-entered location or falls back to district center."""
    if not location_str:
        location_str = district_fallback or "Coimbatore"
    loc_clean = location_str.lower().strip()
    
    # Direct match or partial match
    for key, coords in LOCATION_COORDINATES.items():
        if key in loc_clean or loc_clean in key:
            return coords
            
    # Fallback by district
    dist_clean = (district_fallback or "").lower()
    if "tiruppur" in dist_clean:
        return LOCATION_COORDINATES["tiruppur"]
    elif "erode" in dist_clean:
        return LOCATION_COORDINATES["erode"]
    return LOCATION_COORDINATES["coimbatore"]

def calculate_market_comparison(
    crop_name,
    selected_district,
    selected_market,
    quantity_kg,
    farmer_location,
    target_date=None,
    custom_transport_cost=None,
    custom_other_expenses=None,
    farmer_name="Farmer",
    farmer_phone=""
):
    """
    Performs full market comparison and profit calculations across all 13 mandis.
    
    Formula:
    1. Modal Price is converted from Rs/Quintal to Rs/kg (1 Quintal = 100 kg):
       Price_per_kg = Modal_Price / 100.0
    2. Selling Value = Quantity (kg) * Price_per_kg
    3. Transportation Expenses = Distance (km) * Transport Rate (or custom)
    4. Other Expenses = Quantity (kg) * Rate (or custom)
    5. Final Profit = Selling Value - Transportation Expenses - Other Expenses
    
    Returns comprehensive result with comparisons, recommendation, and saves to DB.
    """
    quantity_kg = float(quantity_kg)
    if quantity_kg <= 0:
        raise ValueError("Crop quantity must be greater than 0 kg.")

    # 1. Fetch transport and expense settings
    settings = {}
    for s in query_db("SELECT setting_key, setting_value FROM app_settings"):
        try:
            settings[s["setting_key"]] = float(s["setting_value"])
        except (ValueError, TypeError):
            settings[s["setting_key"]] = s["setting_value"]

    rate_per_km = settings.get("transport_rate_per_km", 18.0)
    default_other_per_kg = settings.get("other_expenses_per_kg", 0.50)

    # 2. Get farmer coordinates
    f_lat, f_lng = resolve_farmer_coordinates(farmer_location, selected_district)

    # 3. Retrieve all 13 markets
    all_markets = query_db("SELECT id, district_name, market_name, latitude, longitude FROM markets ORDER BY district_name, market_name")
    
    # 4. Retrieve latest prices for this crop
    # Find most recent date available in DB if target_date is not specified or has no records
    query = """
        SELECT dp.*, m.latitude, m.longitude 
        FROM daily_prices dp
        JOIN markets m ON dp.market_name = m.market_name
        WHERE LOWER(dp.crop_name) = LOWER(%s)
    """
    params = [crop_name]

    if target_date:
        query += " AND dp.arrival_date = %s"
        params.append(target_date)

    query += " ORDER BY dp.arrival_date DESC, dp.modal_price DESC"
    
    price_records = query_db(query, tuple(params))
    
    # If no records for specific date, fallback to the latest available date for this crop
    latest_date = None
    if not price_records:
        latest_row = query_db(
            "SELECT MAX(arrival_date) as max_date FROM daily_prices WHERE LOWER(crop_name) = LOWER(%s)",
            (crop_name,),
            one=True
        )
        if latest_row and latest_row.get("max_date"):
            latest_date = latest_row["max_date"]
            price_records = query_db(
                """
                SELECT dp.*, m.latitude, m.longitude 
                FROM daily_prices dp
                JOIN markets m ON dp.market_name = m.market_name
                WHERE LOWER(dp.crop_name) = LOWER(%s) AND dp.arrival_date = %s
                ORDER BY dp.modal_price DESC
                """,
                (crop_name, latest_date)
            )

    # Map prices by market_name
    price_by_market = {}
    for pr in price_records:
        m_name = pr["market_name"]
        if m_name not in price_by_market:  # Keep the most recent/highest
            price_by_market[m_name] = pr

    # 5. Calculate profit metrics for each market
    market_results = []
    
    for m in all_markets:
        m_name = m["market_name"]
        dist_name = m["district_name"]
        m_lat = float(m["latitude"])
        m_lng = float(m["longitude"])

        distance_km = haversine_distance(f_lat, f_lng, m_lat, m_lng)
        
        # Check if we have price data
        price_info = price_by_market.get(m_name)
        
        if price_info:
            modal_price_qtl = float(price_info["modal_price"])
            min_price_qtl = float(price_info["min_price"])
            max_price_qtl = float(price_info["max_price"])
            arrival_date_str = str(price_info["arrival_date"])
            data_source = price_info.get("source", "AGMARKNET")
            has_price = True
        else:
            modal_price_qtl = 0.0
            min_price_qtl = 0.0
            max_price_qtl = 0.0
            arrival_date_str = None
            data_source = "NO_DATA"
            has_price = False

        # Conversion: Rs per Quintal to Rs per kg (1 Quintal = 100 kg)
        price_per_kg = round(modal_price_qtl / 100.0, 2)
        min_price_kg = round(min_price_qtl / 100.0, 2)
        max_price_kg = round(max_price_qtl / 100.0, 2)

        # Selling Value = Quantity (kg) * Price per kg
        selling_value = round(quantity_kg * price_per_kg, 2)

        # Transportation Expenses
        if custom_transport_cost is not None and custom_transport_cost >= 0:
            # If user entered fixed transport cost, adjust slightly by distance ratio or use directly
            transport_cost = round(custom_transport_cost, 2)
        else:
            # Distance-based transport cost
            # Base freight = distance * rate_per_km
            # For heavier loads (> 1000 kg), small scale economy applies
            transport_cost = round(distance_km * rate_per_km, 2)

        # Other Expenses (Loading, unloading, commission, packing)
        if custom_other_expenses is not None and custom_other_expenses >= 0:
            other_expenses = round(custom_other_expenses, 2)
        else:
            other_expenses = round(quantity_kg * default_other_per_kg, 2)

        # Final Profit Formula: Selling Value - Transportation Cost - Other Expenses
        net_profit = round(selling_value - transport_cost - other_expenses, 2) if has_price else 0.0

        is_selected = (m_name.lower() == selected_market.lower())

        market_results.append({
            "market_id": m["id"],
            "market_name": m_name,
            "district_name": dist_name,
            "distance_km": distance_km,
            "has_price": has_price,
            "modal_price_qtl": modal_price_qtl,
            "min_price_qtl": min_price_qtl,
            "max_price_qtl": max_price_qtl,
            "price_per_kg": price_per_kg,
            "min_price_kg": min_price_kg,
            "max_price_kg": max_price_kg,
            "selling_value": selling_value,
            "transport_cost": transport_cost,
            "other_expenses": other_expenses,
            "net_profit": net_profit,
            "arrival_date": arrival_date_str,
            "source": data_source,
            "is_selected": is_selected
        })

    # 6. Determine Best Market Recommendation (highest net profit among mandis with valid price)
    priced_markets = [m for m in market_results if m["has_price"] and m["net_profit"] > 0]
    
    if priced_markets:
        best_market = max(priced_markets, key=lambda x: x["net_profit"])
        best_market_name = best_market["market_name"]
    else:
        best_market = None
        best_market_name = None

    # Mark is_recommended flag
    for m in market_results:
        m["is_recommended"] = (m["market_name"] == best_market_name)

    # 7. Comparison Rationale vs Selected Market
    selected_market_data = next((m for m in market_results if m["is_selected"]), None)
    
    recommendation_summary = None
    if best_market:
        if selected_market_data and selected_market_data["has_price"]:
            profit_diff = best_market["net_profit"] - selected_market_data["net_profit"]
            if best_market["market_name"] == selected_market_data["market_name"]:
                recommendation_summary = (
                    f"Your selected market '{best_market['market_name']}' in {best_market['district_name']} "
                    f"is already the optimal choice! It yields the highest estimated net profit of ₹{best_market['net_profit']:,.2f} "
                    f"after factoring in ₹{best_market['transport_cost']:,.2f} in transport expenses."
                )
            else:
                recommendation_summary = (
                    f"Recommended: Transporting your {quantity_kg:,.0f} kg of {crop_name} to "
                    f"'{best_market['market_name']}' ({best_market['district_name']}) instead of "
                    f"'{selected_market_data['market_name']}' will increase your net profit by ₹{profit_diff:,.2f} "
                    f"(Total Net Profit: ₹{best_market['net_profit']:,.2f} vs ₹{selected_market_data['net_profit']:,.2f})."
                )
        else:
            recommendation_summary = (
                f"Recommended: '{best_market['market_name']}' in {best_market['district_name']} "
                f"offers the best return for {crop_name} with an estimated net profit of ₹{best_market['net_profit']:,.2f}."
            )

    # 8. Store Search and Profit Calculations in MySQL Database
    search_id = None
    try:
        # Create or find farmer
        farmer_id = None
        if farmer_name:
            farmer_row = query_db("SELECT id FROM farmers WHERE name = %s AND location = %s LIMIT 1", (farmer_name, farmer_location), one=True)
            if farmer_row:
                farmer_id = farmer_row["id"]
            else:
                farmer_id = execute_db(
                    "INSERT INTO farmers (name, phone, location, district) VALUES (%s, %s, %s, %s)",
                    (farmer_name, farmer_phone, farmer_location, selected_district),
                    return_last_id=True
                )

        search_id = execute_db(
            """
            INSERT INTO search_history 
            (farmer_id, farmer_name, crop_name, district_name, market_name, quantity_kg, farmer_location, search_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (farmer_id, farmer_name, crop_name, selected_district, selected_market, quantity_kg, farmer_location, date.today()),
            return_last_id=True
        )

        for m in market_results:
            if m["has_price"]:
                execute_db(
                    """
                    INSERT INTO profit_calculations 
                    (search_id, crop_name, quantity_kg, farmer_location, market_name, district_name, 
                     modal_price_quintal, price_per_kg, selling_value, distance_km, transport_cost, 
                     other_expenses, net_profit, is_recommended, calculation_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        search_id, crop_name, quantity_kg, farmer_location, m["market_name"], m["district_name"],
                        m["modal_price_qtl"], m["price_per_kg"], m["selling_value"], m["distance_km"],
                        m["transport_cost"], m["other_expenses"], m["net_profit"], 1 if m["is_recommended"] else 0,
                        date.today()
                    )
                )
    except Exception as e:
        print(f"Error persisting calculation history to database: {e}")

    # Sort results: recommended first, then highest net profit
    sorted_markets = sorted(market_results, key=lambda x: (not x["is_recommended"], -x["net_profit"]))

    return {
        "crop_name": crop_name,
        "quantity_kg": quantity_kg,
        "farmer_location": farmer_location,
        "selected_district": selected_district,
        "selected_market": selected_market,
        "best_market": best_market,
        "selected_market_data": selected_market_data,
        "recommendation_summary": recommendation_summary,
        "markets": sorted_markets,
        "total_markets_compared": len(sorted_markets),
        "priced_markets_count": len(priced_markets),
        "search_id": search_id,
        "calculation_date": str(date.today()),
        "effective_price_date": str(latest_date or date.today())
    }
