# 🌾 Farmer Market Price Assistant

A modern, responsive full-stack web application built with **Python Flask, HTML5, CSS3, JavaScript (ES6+), Chart.js, and MySQL**. 

Specially built for farmers in Tamil Nadu's Western Kongu agricultural belt (**Coimbatore, Tiruppur, and Erode** districts) and across India to track **day-to-day market rates (2020 to Present)**, compare regional prices against **All-India Market Ratings**, leverage **AI crop price predictions**, consult **live meteorological forecasts & agro alerts**, calculate **GPS-based vehicle transport freight**, trade directly on the **buyer-seller marketplace**, manage a personal **farm financial ledger**, and access **crop storage shelf-life recommendations**.

---

## 🌟 8 New Advanced Agricultural Modules

### 1. 🤖 AI-Based Crop Price Prediction
- **Statistical Model**: Time-series exponential smoothing with seasonal decomposition (ES-SD) based on verified AGMARKNET historical daily bulletins.
- **Configurable Horizons**: Select **7 Days, 15 Days, or 30 Days** future forecast.
- **Statistical Confidence Intervals**: Features a 95% upper and lower confidence band rendered dynamically in Chart.js.
- **Harvesting Advisories**: Provides actionable recommendations (*"Harvest & Sell Now"*, *"Hold & Cold Store"*, or *"Stable Trading Range"*) based on momentum.

### 2. 🌦️ Weather Forecast & Agricultural Field Alerts
- **Live Meteorological Telemetry**: Direct integration with the Open-Meteo High-Resolution Model for Coimbatore (11.01°N, 76.95°E), Tiruppur (11.10°N, 77.34°E), and Erode (11.34°N, 77.71°E).
- **7-Day Agro Forecast**: Max/Min temperatures, rainfall probability (%), wind speed, and WMO weather condition icons.
- **Actionable Agro Advisories**:
  - 🚜 *Pesticide & Fertilizer Spraying Window*: Checks wind speed (< 15 km/h) and rain probability to prevent drift or wash-off.
  - 🥥 *Copra & Turmeric Sun-Drying Index*: Monitors solar radiation and humidity for outdoor yard drying in Pollachi and Erode.
  - 🍅 *Fungal Blight & Pest Risk Warning*: Flags high humidity and damp foliage risks for tomato and onion growers.

### 3. 📍 GPS-Based Distance & Vehicle Transportation Cost Calculation
- **HTML5 Geolocation Auto-Detection**: One-click *"Use My GPS Location"* button detects farmer coordinates and finds the nearest regulated market yard.
- **Geodesic Haversine Distance Engine**: Accurate road winding calculations (1.25x factor) to all 13 mandis in Coimbatore, Tiruppur, and Erode.
- **Vehicle Fleet Selector**:
  - 🛺 *Auto / 3-Wheeler*: ₹12/km (< 500 kg capacity)
  - 🚚 *Tata Ace / Small Pickup*: ₹16/km (Standard 1.5-ton capacity)
  - 🚛 *Medium Commercial (407)*: ₹24/km (< 4-ton capacity)
  - 🚛 *Heavy 10-Wheeler Truck*: ₹36/km (10-ton bulk capacity)
- **Direct Formula Integration**:
  $$\text{Final Profit} = \text{Selling Value} - \text{Transport Cost} - \text{Other Expenses}$$

### 4. 🛒 Buyer and Seller Connection Marketplace
- **Direct Trading Board**: Browse farmer sell offers and wholesale buyer purchase requests.
- **Verified Kongu FPOs & Traders**: Includes Pollachi Coconut Producer FPO, Erode Turmeric Farmers Producer Co, Kongu Organic FPO, and regional mills.
- **Direct Middleman-Free Communication**:
  - 📞 Direct Phone Call (`tel:`)
  - 💬 Direct WhatsApp Chat (`https://wa.me/91...`) with pre-filled enquiry message.
- **Post Free Listing Modal**: Farmers and buyers can publish quantity, expected ₹/kg price, and location.

### 5. 🔔 Automatic Crop Price Alerts Through Notifications
- **Real-Time Threshold Monitoring**: Set condition triggers (*Price Rises Above ≥* or *Price Falls Below ≤*) for any mandi and commodity.
- **Web Notification API**: Fires instant native desktop notifications when target prices are reached.
- **Active Alerts Manager**: Inspect active monitors, test triggers, and manage price watches.

### 6. 🎙️ Bilingual Voice Assistant (தமிழ் & English)
- **Floating Action Mic (FAB)**: Accessible across all views with waveform audio visualizer.
- **Web Speech API**: Bilingual speech recognition (`ta-IN` for தமிழ் and `en-IN` for English).
- **Natural Voice Synthesis**: Speaks back market prices, best market recommendations, and weather forecasts in natural spoken Tamil or English.
- **Example Voice Prompts**:
  - *"Tomato price in Pollachi"* / *"பொள்ளாச்சி தக்காளி விலை என்ன"*
  - *"Best market for coconut"* / *"தேங்காய்க்கு சிறந்த சந்தை எது"*
  - *"Weather in Erode"* / *"ஈரோடு வானிலை"*

### 7. 📒 Farmer Income & Expense Management (Farm Ledger)
- **Financial Balance Sheet**: Track operational expenditures vs farm revenues.
- **Categories**: Seeds & Fertilizers, Labor Wages, Diesel & Tractor, Transportation, Irrigation, Crop Sales, and Government Subsidies.
- **KPI Metrics**: Total Revenue (₹), Total Production Costs (₹), Realized Net Profit (₹), and Farm Profit Margin (%).
- **Export**: One-click CSV export for accounting, bank loan documentation, and tax records.

### 8. ❄️ Crop Storage & Shelf-Life Recommendations
- **Post-Harvest Lifespan Calculator**: Enter harvest date to calculate remaining safe trading days and spoilage risk meter.
- **Scientific Parameters**: Optimal temperature (°C) and relative humidity (RH %) guidelines for 8+ major crops.
- **Verified Cold Storage Directory**: Details on Tamil Nadu Government & APMC cold storage facilities in Perundurai (2,500 MT), Pollachi, Kinathukkadavu, Dharapuram, Udumalpet, and Sathyamangalam with phone numbers and capacities.

---

## 🌟 Core Agricultural Engine & Existing Features

### 1. 📅 Day-to-Day Market History (2020 to Now)
- **Year-by-Year & Month-by-Month Explorer**: Select any year (**2020, 2021, 2022, 2023, 2024, 2025, 2026**) and any month (Jan – Dec) to inspect daily historical arrival rates.
- **Day-over-Day (DoD) Change Analytics**:
  - Daily price variation tracking: `+₹X (+Y%)` or `-₹X (-Y%)`.
  - Bullish, Bearish, and Stable market trend indicators.
  - Interactive Day-to-Day Timeline Chart (Modal, Minimum, Maximum prices).
  - Monthly Summary KPIs: Monthly Average Modal Rate, Highest Day of the Month, Lowest Day of the Month, and Net Monthly Gain/Loss.
  - One-click CSV export for any selected month.

### 2. 🇮🇳 All-India Market Ratings & National Benchmarks
- **National Mandi Performance Scores (★ out of 5.0)**:
  - Evaluation based on price premiums, trading volume liquidity, e-NAM digital transparency, and payment turnaround speed.
- **National Major Market Comparison**:
  - **Pollachi Regulated Market** (Coimbatore, Tamil Nadu) — *★ 4.9 (National Copra & Coconut Hub)*
  - **Erode Regulated Market** (Erode, Tamil Nadu) — *★ 4.9 (Global Turmeric Capital)*
  - **Palladam Regulated Market** (Tiruppur, Tamil Nadu) — *★ 4.7 (Shallot & Poultry Maize Center)*
  - **Azadpur APMC Mandi** (Delhi) — *★ 4.8 (Asia's Largest Terminal Market)*
  - **Vashi APMC Mandi** (Navi Mumbai, Maharashtra) — *★ 4.8 (Western Commercial Clearing Hub)*
  - **Lasalgaon APMC** (Nashik, Maharashtra) — *★ 4.8 (Asia's Largest Onion Market)*
  - **Kolar APMC Mandi** (Karnataka) — *★ 4.8 (South India Tomato Terminal)*
  - **Guntur Agricultural Market** (Andhra Pradesh) — *★ 4.8 (Asia's Largest Chilli Yard)*
  - **Nizamabad Regulated Market** (Telangana) — *★ 4.6 (Central Turmeric Hub)*
- **National Price Parity Index**: Shows whether local mandis trade at a premium or discount compared to the All-India composite baseline.

### 3. 🌱 50+ Agricultural Crops & Products
- **Major Vegetables**: Tomato (தக்காளி), Small Pink Onion (சின்ன வெங்காயம்), Potato (உருளைக்கிழங்கு), Green Chilli (பச்சை மிளகாய்), Brinjal (கத்தரிக்காய்), Bhendi/Okra (வெண்டைக்காய்), Cabbage, Cauliflower, Carrot, Drumstick (முருங்கை), Beetroot, Ginger (இஞ்சி), Garlic (பூண்டு).
- **Spices & Plantation**: Turmeric (மஞ்சள்), Coconut (தேங்காய்), Arecanut (பாக்கு), Black Pepper (கருமிளகு), Cardamom (ஏலக்காய்), Coriander Seeds (கொத்தமல்லி), Dry Red Chilli (வற்றல் மிளகாய்).
- **Fruits**: Banana (வாழை - Poovan/Robusta/Nendran), Mango (மாம்பழம்), Pomegranate (மாதுளை), Papaya (பப்பாளி), Lemon (எலுமிச்சை), Guava (கொய்யா).
- **Cereals, Grains & Millets**: Maize / Corn (மக்காச்சோளம்), Paddy / Rice (நெல் / அரிசி), Wheat (கோதுமை), Ragi (கேழ்வரகு), Sorghum (சோளம்), Bajra (கம்பு).
- **Oilseeds & Pulses**: Groundnut (நிலக்கடலை), Sesame / Gingelly (எள்ளு), Sunflower Seeds, Red Gram / Tur Dal (துவரை), Bengal Gram / Chana (கொண்டைக்கடலை), Green Gram / Moong (பாசிப்பயறு), Black Gram / Urad (உளுந்து).
- **Commercial & Fibres**: Cotton (பருத்தி), Sugarcane (கரும்பு), Tapioca (மரவள்ளிக்கிழங்கு).

### 4. 🌾 Price & Profit Assistant (13 Kongu Mandis)
- Dynamically toggles between **Coimbatore, Tiruppur, and Erode**:
  - **Coimbatore**: *Pollachi, Annur, Sulur, Kinathukkadavu*
  - **Tiruppur**: *Udumalpet, Dharapuram, Palladam, Kangayam*
  - **Erode**: *Erode, Gobichettipalayam, Perundurai, Bhavani, Sathyamangalam*
- **Accurate Conversions**: Converts Government Agmarknet rates from ₹/Quintal (100 kg) to ₹/kg.
- **Best Market Recommendation**: Automatically selects and highlights the optimal mandi yielding the highest net profit.

### 5. 📡 Official AGMARKNET (`data.gov.in`) API Integration
- Connects directly to the Government of India Open Government Data platform:
  - **Resource ID**: `9ef84268-d588-465a-a308-a864a43d0070`
  - Zero fabricated prices; arrival dates and last sync timestamps clearly displayed.
  - MySQL deduplication using composite unique keys `(market_name, crop_name, arrival_date)`.

---

## 🔗 Live Website & Links

* **Live Website (GitHub Pages)**: [https://p6409464-hub.github.io/form/](https://p6409464-hub.github.io/form/)
* **GitHub Repository**: [https://github.com/p6409464-hub/form](https://github.com/p6409464-hub/form)
* **Local Web Server**: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🚀 Setup & Run Locally

```powershell
# 1. Navigate to directory
cd C:\Users\Pranesh\.gemini\antigravity\scratch\farmer-market-price-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize & seed MySQL
python seed_data.py

# 4. Run automated test suite (16 tests)
python test_app.py

# 5. Launch Flask Web Application
python app.py
```
