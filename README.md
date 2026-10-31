# 🌾 Farmer Market Price Assistant

A modern, responsive web application built with **Python Flask, HTML5, CSS3, JavaScript (ES6+), Chart.js, and MySQL**. 

Specially built for farmers in Tamil Nadu's Western Kongu agricultural belt (**Coimbatore, Tiruppur, and Erode** districts) and across India to track **day-to-day market rates (2020 to Present)**, compare regional prices against **All-India Market Ratings**, and identify the best mandi to sell their harvest based on real daily agricultural prices from the Government of India's **AGMARKNET / data.gov.in** dataset.

---

## 🌟 Key Features

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
- **Profit Formula**:
  $$\text{Selling Value} = \text{Quantity (kg)} \times \text{Price per kg}$$
  $$\text{Transportation Cost} = \text{Road Distance (km)} \times \text{Freight Rate per km}$$
  $$\text{Other Expenses} = \text{Quantity (kg)} \times \text{Handling Rate per kg}$$
  $$\mathbf{\text{Final Net Profit}} = \mathbf{\text{Selling Value}} - \mathbf{\text{Transportation Cost}} - \mathbf{\text{Other Expenses}}$$
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

# 4. Run automated test suite
python test_app.py

# 5. Launch Flask Web Application
python app.py
```
