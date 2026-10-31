"""
Comprehensive automated integration tests for Farmer Market Price Assistant.
Tests:
- All web routes (/, /dashboard, /prices, /settings)
- REST APIs (/api/districts-and-markets, /api/calculate-profit, /api/dashboard-metrics, /api/mandi-prices)
- Dynamic market selection
- Input validation & error responses
- Quintal to kg conversion & profit formula accuracy
- Best market recommendation selection
"""

import unittest
import json
from datetime import date
from app import app
from db import query_db

class FarmerMarketPriceAssistantTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_01_index_page(self):
        """Test home assistant page loads successfully."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Farmer Market Price Assistant", response.data)
        self.assertIn(b"Coimbatore", response.data)
        self.assertIn(b"Tiruppur", response.data)
        self.assertIn(b"Erode", response.data)

    def test_02_dashboard_page(self):
        """Test analytics dashboard page loads successfully."""
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Agricultural Analytics Dashboard", response.data)

    def test_03_prices_page(self):
        """Test prices explorer page loads successfully."""
        response = self.client.get("/prices")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Mandi Prices Explorer", response.data)

    def test_04_settings_page(self):
        """Test settings page loads successfully."""
        response = self.client.get("/settings")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Agmarknet API Credentials", response.data)

    def test_05_api_districts_and_markets(self):
        """Verify the 3 target districts and exact 13 markets are returned."""
        response = self.client.get("/api/districts-and-markets")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        
        districts = data["data"]
        self.assertIn("Coimbatore", districts)
        self.assertIn("Tiruppur", districts)
        self.assertIn("Erode", districts)

        cbe_markets = [m["name"] for m in districts["Coimbatore"]]
        tpr_markets = [m["name"] for m in districts["Tiruppur"]]
        erd_markets = [m["name"] for m in districts["Erode"]]

        # Verify Coimbatore markets: Pollachi, Annur, Sulur, Kinathukkadavu
        for m in ["Pollachi", "Annur", "Sulur", "Kinathukkadavu"]:
            self.assertIn(m, cbe_markets)

        # Verify Tiruppur markets: Udumalpet, Dharapuram, Palladam, Kangayam
        for m in ["Udumalpet", "Dharapuram", "Palladam", "Kangayam"]:
            self.assertIn(m, tpr_markets)

        # Verify Erode markets: Erode, Gobichettipalayam, Perundurai, Bhavani, Sathyamangalam
        for m in ["Erode", "Gobichettipalayam", "Perundurai", "Bhavani", "Sathyamangalam"]:
            self.assertIn(m, erd_markets)

    def test_06_calculate_profit_formula_and_recommendation(self):
        """
        Verify profit calculator formula:
        Selling Value = Quantity (kg) * (Modal Price / 100)
        Final Profit = Selling Value - Transport Cost - Other Expenses
        """
        payload = {
            "crop_name": "Tomato",
            "district_name": "Coimbatore",
            "market_name": "Pollachi",
            "date": str(date.today()),
            "quantity_kg": 1000,
            "farmer_location": "Pollachi",
            "farmer_name": "K. Murugan"
        }
        response = self.client.post(
            "/api/calculate-profit",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        
        calc = data["data"]
        self.assertEqual(calc["quantity_kg"], 1000)
        self.assertIsNotNone(calc["best_market"])
        self.assertGreater(len(calc["markets"]), 0)

        # Verify formula on best market
        best = calc["best_market"]
        expected_selling = round(1000 * (best["modal_price_qtl"] / 100.0), 2)
        self.assertEqual(best["selling_value"], expected_selling)
        
        expected_profit = round(best["selling_value"] - best["transport_cost"] - best["other_expenses"], 2)
        self.assertEqual(best["net_profit"], expected_profit)
        self.assertTrue(best["is_recommended"])

    def test_07_input_validation(self):
        """Verify validation errors for bad or missing inputs."""
        # 1. Negative quantity
        bad_qty_payload = {
            "crop_name": "Tomato",
            "district_name": "Coimbatore",
            "market_name": "Pollachi",
            "quantity_kg": -50
        }
        res = self.client.post("/api/calculate-profit", data=json.dumps(bad_qty_payload), content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("quantity", json.loads(res.data)["error"].lower())

        # 2. Missing crop name
        no_crop_payload = {
            "crop_name": "",
            "district_name": "Coimbatore",
            "market_name": "Pollachi",
            "quantity_kg": 100
        }
        res2 = self.client.post("/api/calculate-profit", data=json.dumps(no_crop_payload), content_type="application/json")
        self.assertEqual(res2.status_code, 400)
        self.assertIn("crop", json.loads(res2.data)["error"].lower())

    def test_08_dashboard_metrics_api(self):
        """Test aggregated metrics and chart dataset for dashboard."""
        response = self.client.get("/api/dashboard-metrics?crop=Tomato")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("metrics", data)
        self.assertIn("market_comparison", data)
        self.assertIn("price_trend", data)
        self.assertIn("recent_searches", data)

        # Ensure KPI metrics are present
        m = data["metrics"]
        self.assertIn("total_searches", m)
        self.assertIn("total_prices_records", m)
        self.assertIn("highest_price", m)
        self.assertIn("top_recommended_market", m)

    def test_09_mandi_prices_filter_api(self):
        """Test filtering mandi prices by district and commodity."""
        response = self.client.get("/api/mandi-prices?district=Coimbatore&crop=Tomato")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)
        
        for item in data["data"]:
            self.assertEqual(item["district_name"], "Coimbatore")
            self.assertEqual(item["crop_name"], "Tomato")
            self.assertGreater(item["modal_price_kg"], 0)

    def test_10_ai_price_prediction_api(self):
        """Test AI-based crop price prediction with confidence bounds and harvesting advisory."""
        response = self.client.get("/api/ai-price-prediction?crop=Tomato&market=Pollachi&days=15")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        pred = data["data"]
        self.assertEqual(pred["crop_name"], "Tomato")
        self.assertEqual(pred["market_name"], "Pollachi")
        self.assertEqual(pred["days_ahead"], 15)
        self.assertGreater(pred["current_price"], 0)
        self.assertGreater(len(pred["forecast_points"]), 0)
        self.assertIn("advisory_action", pred)
        self.assertIn("trend_direction", pred)

    def test_11_weather_forecast_api(self):
        """Test live/fallback meteorological forecast and agricultural advisories."""
        response = self.client.get("/api/weather-forecast?location=Coimbatore")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("daily_forecast", data)
        self.assertIn("agricultural_alerts", data)
        self.assertIn("current", data)
        self.assertGreater(len(data["daily_forecast"]), 0)
        self.assertGreater(len(data["agricultural_alerts"]), 0)

    def test_12_gps_route_cost_api(self):
        """Test GPS geodesic distance and vehicle freight rate calculations across 13 mandis."""
        payload = {
            "latitude": 10.6585,
            "longitude": 77.0084,
            "quantity_kg": 2000,
            "vehicle_type": "mini_truck"
        }
        response = self.client.post(
            "/api/gps-route-cost",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["markets"]), 13)
        # Verify nearest market has lowest distance
        nearest = data["markets"][0]
        self.assertEqual(nearest["market_name"], "Pollachi")
        self.assertLessEqual(nearest["distance_km"], 5.0)
        self.assertGreater(nearest["total_transport_cost"], 0)

    def test_13_marketplace_listings_api(self):
        """Test browsing and posting buyer/seller listings."""
        # 1. GET listings
        get_res = self.client.get("/api/marketplace/listings")
        self.assertEqual(get_res.status_code, 200)
        data = json.loads(get_res.data)
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)

        # 2. POST new listing
        new_listing = {
            "listing_type": "SELL",
            "user_name": "Test Farmer",
            "user_phone": "9876543210",
            "user_role": "Farmer",
            "district": "Coimbatore",
            "location": "Pollachi Rural",
            "crop_name": "Tomato",
            "variety": "Standard Hybrid",
            "quantity_kg": 1500,
            "price_per_kg": 32.50,
            "notes": "Automated test listing"
        }
        post_res = self.client.post(
            "/api/marketplace/listings",
            data=json.dumps(new_listing),
            content_type="application/json"
        )
        self.assertEqual(post_res.status_code, 200)
        pdata = json.loads(post_res.data)
        self.assertTrue(pdata["success"])
        self.assertIn("listing_id", pdata)

    def test_14_price_alerts_api(self):
        """Test configuring and triggering price threshold alerts."""
        # 1. POST new price alert
        alert_payload = {
            "farmer_name": "Test Alert User",
            "contact": "9998887776",
            "crop_name": "Tomato",
            "market_name": "Pollachi",
            "condition_type": "ABOVE",
            "target_price_per_kg": 20.0
        }
        res = self.client.post(
            "/api/price-alerts",
            data=json.dumps(alert_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)["success"])

        # 2. Check alerts
        chk_res = self.client.get("/api/check-alerts")
        self.assertEqual(chk_res.status_code, 200)
        chk_data = json.loads(chk_res.data)
        self.assertTrue(chk_data["success"])

    def test_15_farm_ledger_api(self):
        """Test recording farm income/expense transactions and computing financial metrics."""
        # 1. POST an income entry
        entry_payload = {
            "entry_type": "INCOME",
            "category": "Crop Sale",
            "title": "Tomato Sale 1000kg",
            "crop_name": "Tomato",
            "amount": 35000,
            "notes": "Direct mandi sale"
        }
        res = self.client.post(
            "/api/farm-ledger",
            data=json.dumps(entry_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)["success"])

        # 2. GET summary
        get_res = self.client.get("/api/farm-ledger")
        self.assertEqual(get_res.status_code, 200)
        data = json.loads(get_res.data)
        self.assertTrue(data["success"])
        self.assertIn("summary", data)
        self.assertIn("total_income", data["summary"])
        self.assertIn("total_expense", data["summary"])
        self.assertIn("net_profit", data["summary"])
        self.assertIn("profit_margin_pct", data["summary"])

    def test_16_storage_recommendations_api(self):
        """Test post-harvest shelf life calculator and cold storage directory."""
        res = self.client.get("/api/storage-recommendations?crop=Tomato&storage_type=ambient")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("shelf_life", data)
        self.assertIn("cold_storages", data)
        self.assertGreater(len(data["cold_storages"]), 0)

if __name__ == "__main__":
    unittest.main()
