"""
Farmer Market Price Assistant - Main Flask Application
Developed for Tamil Nadu Farmers (Coimbatore, Tiruppur, Erode)
"""

import os
import json
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from config import Config
from db import init_db, query_db, execute_db
from agmarknet_service import (
    sync_agmarknet_api,
    get_last_sync_info,
    get_active_api_key,
    save_active_api_key
)
from profit_service import calculate_market_comparison

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database tables exist on startup
try:
    init_db()
except Exception as e:
    print(f"Warning on init_db: {e}")

# Context processor for global template variables
@app.context_processor
def inject_global_vars():
    sync_info = get_last_sync_info()
    return {
        "sync_info": sync_info,
        "now": datetime.now(),
        "today_date": str(date.today())
    }

# =========================================================================
# Web Page Routes
# =========================================================================

@app.route("/")
def index():
    """Main Market Price Assistant & Profit Calculator Page"""
    districts = query_db("SELECT id, name FROM districts ORDER BY name")
    crops = query_db("SELECT id, name, tamil_name, category FROM crops ORDER BY name")
    
    # Pre-fetch target markets map for client-side instant switching
    markets = query_db("SELECT id, district_name, market_name FROM markets ORDER BY district_name, market_name")
    markets_by_district = {}
    for m in markets:
        dist = m["district_name"]
        if dist not in markets_by_district:
            markets_by_district[dist] = []
        markets_by_district[dist].append(m["market_name"])

    # High-level stats for top banner
    total_crops = len(crops)
    total_markets = len(markets)
    latest_update = query_db("SELECT MAX(arrival_date) as latest FROM daily_prices", one=True)

    return render_template(
        "index.html",
        districts=districts,
        crops=crops,
        markets_by_district=markets_by_district,
        total_crops=total_crops,
        total_markets=total_markets,
        latest_date=latest_update["latest"] if latest_update else date.today()
    )

@app.route("/dashboard")
def dashboard():
    """Analytics Dashboard with Key Metrics, Charts & Price Trends"""
    return render_template("dashboard.html")

@app.route("/prices")
def prices():
    """Live Agmarknet Prices Explorer with filters"""
    districts = query_db("SELECT id, name FROM districts ORDER BY name")
    crops = query_db("SELECT id, name, tamil_name FROM crops ORDER BY name")
    markets = query_db("SELECT DISTINCT market_name, district_name FROM markets ORDER BY market_name")
    return render_template("prices.html", districts=districts, crops=crops, markets=markets)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    """AGMARKNET API Key & Transport Rate Settings"""
    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        transport_rate = request.form.get("transport_rate", "").strip()
        other_expenses_rate = request.form.get("other_expenses_rate", "").strip()

        if api_key is not None:
            save_active_api_key(api_key)
        
        if transport_rate:
            try:
                rate_val = float(transport_rate)
                execute_db(
                    "UPDATE app_settings SET setting_value = %s WHERE setting_key = 'transport_rate_per_km'",
                    (f"{rate_val:.2f}",)
                )
            except ValueError:
                flash("Invalid transport rate value.", "danger")

        if other_expenses_rate:
            try:
                other_val = float(other_expenses_rate)
                execute_db(
                    "UPDATE app_settings SET setting_value = %s WHERE setting_key = 'other_expenses_per_kg'",
                    (f"{other_val:.2f}",)
                )
            except ValueError:
                flash("Invalid other expenses rate value.", "danger")

        flash("Settings saved successfully!", "success")
        return redirect(url_for("settings"))

    # GET request
    settings_rows = query_db("SELECT setting_key, setting_value FROM app_settings")
    settings_dict = {row["setting_key"]: row["setting_value"] for row in settings_rows}
    
    sync_logs = query_db("SELECT * FROM api_sync_logs ORDER BY synced_at DESC LIMIT 15")
    current_key = get_active_api_key()

    return render_template(
        "settings.html",
        settings=settings_dict,
        api_key=current_key,
        sync_logs=sync_logs
    )

# =========================================================================
# REST API Endpoints
# =========================================================================

@app.route("/api/districts-and-markets")
def api_districts_and_markets():
    """Returns districts and their assigned markets."""
    markets = query_db("SELECT id, district_name, market_name FROM markets ORDER BY district_name, market_name")
    result = {}
    for m in markets:
        dist = m["district_name"]
        if dist not in result:
            result[dist] = []
        result[dist].append({
            "id": m["id"],
            "name": m["market_name"]
        })
    return jsonify({"success": True, "data": result})

@app.route("/api/calculate-profit", methods=["POST"])
def api_calculate_profit():
    """
    Validates user inputs and runs Market Comparison & Profit Recommendation.
    """
    data = request.get_json() or {}
    
    # Required inputs validation
    crop_name = (data.get("crop_name") or "").strip()
    district_name = (data.get("district_name") or "").strip()
    market_name = (data.get("market_name") or "").strip()
    date_val = (data.get("date") or "").strip()
    farmer_location = (data.get("farmer_location") or "").strip()
    
    try:
        quantity_kg = float(data.get("quantity_kg", 0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Please provide a valid crop quantity in kilograms."}), 400

    if not crop_name:
        return jsonify({"success": False, "error": "Please select or enter a crop name."}), 400
    if not district_name:
        return jsonify({"success": False, "error": "Please select a district."}), 400
    if not market_name:
        return jsonify({"success": False, "error": "Please select a market."}), 400
    if quantity_kg <= 0:
        return jsonify({"success": False, "error": "Crop quantity must be greater than 0 kg."}), 400
    if not farmer_location:
        farmer_location = market_name  # default to market town

    custom_transport = None
    if data.get("custom_transport_cost") is not None and data.get("custom_transport_cost") != "":
        try:
            custom_transport = float(data.get("custom_transport_cost"))
        except ValueError:
            pass

    custom_other = None
    if data.get("custom_other_expenses") is not None and data.get("custom_other_expenses") != "":
        try:
            custom_other = float(data.get("custom_other_expenses"))
        except ValueError:
            pass

    try:
        results = calculate_market_comparison(
            crop_name=crop_name,
            selected_district=district_name,
            selected_market=market_name,
            quantity_kg=quantity_kg,
            farmer_location=farmer_location,
            target_date=date_val if date_val else None,
            custom_transport_cost=custom_transport,
            custom_other_expenses=custom_other,
            farmer_name=data.get("farmer_name", "Farmer"),
            farmer_phone=data.get("farmer_phone", "")
        )
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/dashboard-metrics")
def api_dashboard_metrics():
    """
    Returns aggregated metrics and charts dataset:
    - Total markets searched
    - Available crop prices
    - Highest market price
    - Best profitable market
    - Comparison charts dataset
    - Daily price history
    """
    # 1. Total markets searched count
    searches_count = query_db("SELECT COUNT(*) as count FROM search_history", one=True)["count"]
    
    # 2. Total active crop prices
    total_prices_count = query_db("SELECT COUNT(*) as count FROM daily_prices", one=True)["count"]

    # 3. Highest market price currently recorded
    highest_price_row = query_db(
        """
        SELECT crop_name, market_name, district_name, modal_price, arrival_date 
        FROM daily_prices 
        ORDER BY modal_price DESC LIMIT 1
        """,
        one=True
    )

    # 4. Most recommended best profitable market
    top_recommended_row = query_db(
        """
        SELECT market_name, district_name, COUNT(*) as rec_count, AVG(net_profit) as avg_profit
        FROM profit_calculations
        WHERE is_recommended = 1
        GROUP BY market_name, district_name
        ORDER BY rec_count DESC, avg_profit DESC LIMIT 1
        """,
        one=True
    )

    # 5. Average modal price by crop (for Bar Chart)
    crop_avg_prices = query_db(
        """
        SELECT crop_name, ROUND(AVG(modal_price), 2) as avg_modal, ROUND(AVG(modal_price)/100.0, 2) as avg_per_kg
        FROM daily_prices
        GROUP BY crop_name
        ORDER BY avg_modal DESC
        LIMIT 10
        """
    )

    # 6. Market-level price comparison for major staple (Tomato / Turmeric / Coconut)
    active_crop = request.args.get("crop", "Tomato")
    market_comparison_data = query_db(
        """
        SELECT dp.market_name, dp.district_name, dp.modal_price, ROUND(dp.modal_price/100.0, 2) as price_per_kg, dp.arrival_date
        FROM daily_prices dp
        WHERE LOWER(dp.crop_name) = LOWER(%s)
        GROUP BY dp.market_name
        ORDER BY dp.modal_price DESC
        """,
        (active_crop,)
    )

    # 7. Price history trend for the past 7 arrival dates
    price_trend = query_db(
        """
        SELECT arrival_date, ROUND(AVG(modal_price), 2) as avg_modal, ROUND(MAX(modal_price), 2) as max_modal, ROUND(MIN(modal_price), 2) as min_modal
        FROM daily_prices
        WHERE LOWER(crop_name) = LOWER(%s)
        GROUP BY arrival_date
        ORDER BY arrival_date ASC
        LIMIT 10
        """,
        (active_crop,)
    )

    # 8. Recent search history
    recent_searches = query_db(
        """
        SELECT sh.*, pc.net_profit, pc.is_recommended, pc.modal_price_quintal
        FROM search_history sh
        LEFT JOIN profit_calculations pc ON sh.id = pc.search_id AND pc.is_recommended = 1
        ORDER BY sh.created_at DESC
        LIMIT 8
        """
    )

    return jsonify({
        "success": True,
        "metrics": {
            "total_searches": searches_count,
            "total_prices_records": total_prices_count,
            "highest_price": highest_price_row,
            "top_recommended_market": top_recommended_row,
            "active_crop": active_crop
        },
        "crop_averages": crop_avg_prices,
        "market_comparison": market_comparison_data,
        "price_trend": price_trend,
        "recent_searches": recent_searches
    })

@app.route("/api/mandi-prices")
def api_mandi_prices():
    """
    Searchable, filterable list of daily market prices.
    Filters: district, market, crop, date.
    """
    district = request.args.get("district", "").strip()
    market = request.args.get("market", "").strip()
    crop = request.args.get("crop", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    
    query = "SELECT * FROM daily_prices WHERE 1=1"
    params = []
    
    if district:
        query += " AND district_name = %s"
        params.append(district)
    if market:
        query += " AND market_name = %s"
        params.append(market)
    if crop:
        query += " AND crop_name = %s"
        params.append(crop)
    if start_date:
        query += " AND arrival_date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND arrival_date <= %s"
        params.append(end_date)
        
    query += " ORDER BY arrival_date DESC, modal_price DESC LIMIT 200"
    
    rows = query_db(query, tuple(params))
    
    # Format per-kg prices
    for r in rows:
        r["min_price_kg"] = round(float(r["min_price"]) / 100.0, 2)
        r["max_price_kg"] = round(float(r["max_price"]) / 100.0, 2)
        r["modal_price_kg"] = round(float(r["modal_price"]) / 100.0, 2)
        r["arrival_date"] = str(r["arrival_date"])
        
    return jsonify({"success": True, "data": rows, "count": len(rows)})

@app.route("/api/sync-agmarknet", methods=["POST"])
def api_sync_agmarknet():
    """
    Triggers live synchronization with the official AGMARKNET API on data.gov.in.
    Accepts optional custom api_key and filters.
    """
    data = request.get_json() or {}
    custom_key = data.get("api_key")
    crop = data.get("crop")
    district = data.get("district")
    
    sync_result = sync_agmarknet_api(
        custom_key=custom_key,
        crop_filter=crop,
        district_filter=district
    )
    return jsonify(sync_result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
