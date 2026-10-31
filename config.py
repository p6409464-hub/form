import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "farmer-assistant-secret-2026")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    PORT = int(os.getenv("PORT", 5000))
    
    # Database Settings
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "farmer_market_db")
    
    # Official AGMARKNET / data.gov.in API
    DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY", "").strip()
    AGMARKNET_RESOURCE_ID = os.getenv("AGMARKNET_RESOURCE_ID", "9ef84268-d588-465a-a308-a864a43d0070")
    AGMARKNET_API_BASE_URL = os.getenv("AGMARKNET_API_BASE_URL", "https://api.data.gov.in/resource")
    
    # Target Districts & Markets
    TARGET_DISTRICTS = {
        "Coimbatore": ["Pollachi", "Annur", "Sulur", "Kinathukkadavu"],
        "Tiruppur": ["Udumalpet", "Dharapuram", "Palladam", "Kangayam"],
        "Erode": ["Erode", "Gobichettipalayam", "Perundurai", "Bhavani", "Sathyamangalam"]
    }
