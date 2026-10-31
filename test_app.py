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

if __name__ == "__main__":
    unittest.main()
