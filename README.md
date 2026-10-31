# 🌾 Farmer Market Price Assistant

A modern, responsive web application developed using **Python Flask, HTML5, CSS3, JavaScript (ES6+), Chart.js, and MySQL**. 

Specially built for farmers in the Western Kongu agricultural belt of Tamil Nadu (**Coimbatore, Tiruppur, and Erode** districts) to identify the best regulated market (Mandi) to sell their harvest by comparing real-world daily agricultural prices from the Government of India's **AGMARKNET / data.gov.in** dataset and calculating estimated final net profit after transportation and handling expenses.

---

## 🌟 Key Features

### 1. Farmer Input & Dynamic Market Chaining
- Intuitive, mobile-responsive input form for:
  - **Crop Name**: Searchable selector with quick chips for Kongu staples (*Tomato, Coconut, Turmeric, Onion, Banana, Maize, Groundnut, etc.*).
  - **District Name**: Dynamically toggles between **Coimbatore, Tiruppur, and Erode**.
  - **Market Name**: Dynamically updates mandis based on selected district:
    - **Coimbatore**: *Pollachi, Annur, Sulur, Kinathukkadavu*
    - **Tiruppur**: *Udumalpet, Dharapuram, Palladam, Kangayam*
    - **Erode**: *Erode, Gobichettipalayam, Perundurai, Bhavani, Sathyamangalam*
  - **Date Picker**: Defaults to current date for latest daily arrival rates.
  - **Crop Quantity (in kg)**: Easy input for harvest volume.
  - **Farmer Location**: Autofill suggestions for regional towns/villages to calculate accurate road distance to each of the 13 mandis.

### 2. Real-World Daily AGMARKNET API Integration
- Connects directly to the official Open Government Data (OGD) platform API:
  - **Endpoint**: `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`
  - **Retrieves**: Crop Name, District, Market Name, Arrival Date, Minimum Price, Maximum Price, Modal Price.
  - **Transparent Data Integrity**: Honest reporting of real government records, clear display of arrival dates and last sync timestamps. Zero fictitious price generation.
  - **Intelligent Deduplication**: Avoids duplicate entries in MySQL with composite unique keys `(market_name, crop_name, arrival_date)`.
  - **Robust Error Handling**: Gracefully handles network timeouts, API key requirements, and missing commodity arrival reports.

### 3. Market Comparison Engine
- Compares prices across all **13 regulated mandis** in Coimbatore, Tiruppur, and Erode in a responsive, filterable data table.
- Accurately converts government rates from **₹ per Quintal (100 kg)** to **₹ per kilogram**:
  $$\text{Price per kg} = \frac{\text{Modal Price (\text{₹}/Quintal)}}{100}$$
- Shows road distance (km), estimated freight, handling expenses, and net profit for every mandi.

### 4. Profit Calculator & Best Market Recommendation
- **Formula**:
  $$\text{Selling Value} = \text{Crop Quantity (kg)} \times \text{Price per kg}$$
  $$\text{Transportation Cost} = \text{Distance (km)} \times \text{Rate per km}$$
  $$\text{Other Expenses} = \text{Crop Quantity (kg)} \times \text{Rate per kg}$$
  $$\mathbf{\text{Final Profit}} = \mathbf{\text{Selling Value}} - \mathbf{\text{Transportation Cost}} - \mathbf{\text{Other Expenses}}$$
- **Automated Recommendation**: Instantly highlights the market yielding the highest final profit.
- Explains the economic rationale: Compares the recommended mandi against the farmer's local base mandi (e.g. extra profit generated vs. extra transportation incurred).

### 5. Interactive Analytics Dashboard
- **4 Key KPI Cards**:
  - Total Markets Searched
  - Available Crop Prices
  - Highest Market Price
  - Best Profitable Market
- **Visual Charts (Chart.js)**:
  - *Mandi Price Comparison Bar Chart* (color-coded by district)
  - *Daily Price History & Trend Line Chart* (Min, Modal, Max rate movements over time)
  - *Regional Commodity Benchmark Bar Chart*
- Search history and calculation logs stored in MySQL.

### 6. Modern Agricultural Design
- Clean, farmer-friendly green and white palette (`#15803d`, `#14532d`, `#dcfce7`).
- Mobile-first responsive layout tailored for farmers using smartphones in the field.
- Print-ready profit summary and one-click **CSV Data Export**.

---

## 🏗️ Architecture & Database Design

### Target Districts and Regulated Mandis

| District | Regulated Mandis (Markets) | Regional Specialization |
| :--- | :--- | :--- |
| **Coimbatore** | Pollachi, Annur, Sulur, Kinathukkadavu | Coconut hub, Vegetables, Tomato |
| **Tiruppur** | Udumalpet, Dharapuram, Palladam, Kangayam | Shallots / Small Onion, Maize, Copra |
| **Erode** | Erode, Gobichettipalayam, Perundurai, Bhavani, Sathyamangalam | World-famous Turmeric, Banana, Tapioca |

### MySQL Database Schema (`farmer_market_db`)
- `districts`: 3 Target Tamil Nadu districts.
- `markets`: 13 Mandis with geographical latitude and longitude coordinates.
- `crops`: Kongu regional crops with English and Tamil names.
- `daily_prices`: Official Agmarknet prices (`market_name`, `district_name`, `crop_name`, `variety`, `arrival_date`, `min_price`, `max_price`, `modal_price`, `source`) with `UNIQUE (market_name, crop_name, arrival_date)`.
- `farmers`: Farmer profile and village/town details.
- `search_history`: Search log containing crop, quantity, and date.
- `profit_calculations`: Breakdown of selling value, freight, cess, and net profit.
- `api_sync_logs`: Audit log of Government API synchronization calls.
- `app_settings`: Configurable transport rate, cess rate, and API keys.

---

## 🚀 Quick Setup & Installation

### Prerequisites
- Python 3.10+
- MySQL or MariaDB (e.g. XAMPP on port 3306)
- Git (optional)

### 1. Clone / Navigate to Project Directory
```powershell
cd C:\Users\Pranesh\.gemini\antigravity\scratch\farmer-market-price-assistant
```

### 2. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Start MySQL / MariaDB Server
If using XAMPP:
- Open XAMPP Control Panel and start MySQL, or ensure mysqld is running on port 3306.
- The default credentials in `.env` are `DB_HOST=127.0.0.1`, `DB_PORT=3306`, `DB_USER=root`, `DB_PASSWORD=`.

### 4. Initialize Database and Seed Data
Run the seeding script to create the schema and load baseline official Agmarknet published prices for the 13 mandis:
```powershell
python seed_data.py
```

### 5. Configure AGMARKNET API Key (Optional for Live Sync)
Register for a free account at [data.gov.in](https://data.gov.in/) and obtain your API key.
Add it to `.env`:
```env
DATA_GOV_IN_API_KEY=your_api_key_here
```
*(Or input it directly via the web app under **API & Settings**).*

### 6. Run the Flask Web Application
```powershell
python app.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```

---

## 📱 Application Pages

1. **Market Assistant (`/`)**: Main interactive tool with dynamic dropdowns, profit calculator, best mandi recommendation card, and comparison table.
2. **Mandi Prices Explorer (`/prices`)**: Full searchable list of daily Agmarknet mandi arrivals with filters and CSV export.
3. **Analytics Dashboard (`/dashboard`)**: KPI metric cards, Chart.js visual price comparisons across mandis, trend lines, and recent searches.
4. **API & Settings (`/settings`)**: Government API configuration, freight rate settings, and sync audit logs.

---

## 🧪 Testing the Complete Application

1. **Test Dynamic Chaining**: On the home page, change the District from **Coimbatore** to **Tiruppur** or **Erode**. Verify the Market dropdown updates dynamically.
2. **Test Profit Calculation**: Enter `1500` kg of `Tomato` in `Pollachi`, and click **Compare Markets & Calculate Profit**. Verify that:
   - Selling value converts correctly (`Modal Price / 100 * 1500 kg`).
   - Transport expenses and net profit calculate accurately.
   - The best market recommendation banner highlights the optimal mandi.
3. **Test Dashboard & Charts**: Navigate to `/dashboard` to inspect the 4 KPI stat cards, interactive Chart.js bar chart, and price history line chart.
4. **Test Live Mandi Prices**: Visit `/prices` to filter records by commodity or district.
5. **Test Official Sync**: Click **Sync API** in the navigation header to test live communication with data.gov.in.
