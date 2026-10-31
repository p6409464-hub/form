"""
Agmarknet / data.gov.in API Integration Service
Handles:
- Official Government of India Data API consumption (Resource: 9ef84268-d588-465a-a308-a864a43d0070)
- Validation, error handling, date parsing, and deduplication
- Synchronizing prices into MySQL daily_prices
- Safe caching and transparent reporting of API status & arrival dates
"""

import os
import json
import logging
from datetime import datetime, date, timedelta
import requests
from config import Config
from db import query_db, execute_db, get_db_connection

logger = logging.getLogger(__name__)

# Canonical 13 target markets in Coimbatore, Tiruppur, Erode
TARGET_MARKETS = {
    "coimbatore": ["Pollachi", "Annur", "Sulur", "Kinathukkadavu"],
    "tiruppur": ["Udumalpet", "Dharapuram", "Palladam", "Kangayam"],
    "erode": ["Erode", "Gobichettipalayam", "Perundurai", "Bhavani", "Sathyamangalam"]
}

ALL_TARGET_MANDIS = [m.lower() for markets in TARGET_MARKETS.values() for m in markets]

def get_active_api_key():
    """Retrieves API key from app_settings DB table first, fallback to Config."""
    try:
        setting = query_db("SELECT setting_value FROM app_settings WHERE setting_key = 'data_gov_in_api_key'", one=True)
        if setting and setting.get("setting_value") and setting["setting_value"].strip():
            return setting["setting_value"].strip()
    except Exception as e:
        logger.warning(f"Failed to read API key from DB: {e}")
    
    return Config.DATA_GOV_IN_API_KEY.strip()

def save_active_api_key(api_key):
    """Saves user-configured API key into app_settings table."""
    execute_db(
        """
        INSERT INTO app_settings (setting_key, setting_value, description)
        VALUES ('data_gov_in_api_key', %s, 'API Key for data.gov.in official Agmarknet endpoint')
        ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value), updated_at = CURRENT_TIMESTAMP
        """,
        (api_key.strip(),)
    )

def parse_arrival_date(date_str):
    """Parses date string into date object (handles DD/MM/YYYY, YYYY-MM-DD, etc.)."""
    if not date_str:
        return date.today()
    if isinstance(date_str, (date, datetime)):
        return date_str if isinstance(date_str, date) else date_str.date()
    
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            continue
    return date.today()

def normalize_market_name(raw_name):
    """Matches raw Agmarknet market name to canonical 13 target markets if matched."""
    if not raw_name:
        return None
    raw_lower = raw_name.lower().strip()
    
    # Direct match or partial match
    canonical_list = [
        "Pollachi", "Annur", "Sulur", "Kinathukkadavu",
        "Udumalpet", "Dharapuram", "Palladam", "Kangayam",
        "Erode", "Gobichettipalayam", "Perundurai", "Bhavani", "Sathyamangalam"
    ]
    for canon in canonical_list:
        if canon.lower() in raw_lower or raw_lower in canon.lower():
            return canon
    return raw_name.strip()

def sync_agmarknet_api(custom_key=None, crop_filter=None, district_filter=None):
    """
    Calls the official Government of India Agmarknet endpoint on data.gov.in:
    Endpoint: https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
    
    Parameters:
    - custom_key: Optional API key override
    - crop_filter: Optional commodity name filter
    - district_filter: Optional district filter
    
    Returns structured dict with status, count, and message.
    """
    api_key = custom_key.strip() if custom_key else get_active_api_key()
    
    if not api_key:
        msg = (
            "AGMARKNET API Key is not configured. "
            "Please register for a free API key at https://data.gov.in/ and save it in Settings or your .env file."
        )
        _log_sync("FAILED", 0, 0, msg)
        return {
            "success": False,
            "status": "API_KEY_REQUIRED",
            "message": msg,
            "records_fetched": 0,
            "records_inserted": 0
        }

    url = f"{Config.AGMARKNET_API_BASE_URL}/{Config.AGMARKNET_RESOURCE_ID}"
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": 1000,
        "filters[state]": "Tamil Nadu"
    }

    if district_filter and district_filter.lower() in ("coimbatore", "tiruppur", "erode"):
        params["filters[district]"] = district_filter
    if crop_filter:
        params["filters[commodity]"] = crop_filter

    headers = {
        "User-Agent": "FarmerMarketPriceAssistant/1.0 (TamilNadu-KonguRegion)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=12)
        if response.status_code == 401 or "Authorization field missing" in response.text or "Invalid API Key" in response.text:
            err = "Invalid or unauthorized API key provided for data.gov.in."
            _log_sync("FAILED", 0, 0, err)
            return {
                "success": False,
                "status": "INVALID_API_KEY",
                "message": err,
                "records_fetched": 0,
                "records_inserted": 0
            }

        if response.status_code != 200:
            err = f"data.gov.in API returned HTTP {response.status_code}: {response.text[:200]}"
            _log_sync("FAILED", 0, 0, err)
            return {
                "success": False,
                "status": "API_ERROR",
                "message": err,
                "records_fetched": 0,
                "records_inserted": 0
            }

        payload = response.json()
        records = payload.get("records", [])

        if not records:
            msg = "Official AGMARKNET API responded successfully, but no records were reported for Tamil Nadu for this query."
            _log_sync("NO_DATA", 0, 0, msg)
            return {
                "success": True,
                "status": "NO_RECORDS",
                "message": msg,
                "records_fetched": 0,
                "records_inserted": 0
            }

        # Lookup market IDs
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, market_name, district_name FROM markets")
                m_rows = cursor.fetchall()
                market_lookup = {row["market_name"].lower(): (row["id"], row["district_name"], row["market_name"]) for row in m_rows}

                inserted_count = 0
                updated_count = 0

                for r in records:
                    raw_market = r.get("market", "")
                    canon_market = normalize_market_name(raw_market)
                    if not canon_market:
                        continue
                    
                    market_info = market_lookup.get(canon_market.lower())
                    market_id = market_info[0] if market_info else None
                    district_name = market_info[1] if market_info else r.get("district", "Tamil Nadu")
                    official_market_name = market_info[2] if market_info else canon_market

                    crop_name = r.get("commodity", "").strip()
                    variety = r.get("variety", "General").strip()
                    arrival_date = parse_arrival_date(r.get("arrival_date"))
                    
                    try:
                        min_p = float(r.get("min_price", 0))
                        max_p = float(r.get("max_price", 0))
                        modal_p = float(r.get("modal_price", 0))
                    except (ValueError, TypeError):
                        continue

                    if modal_p <= 0 and (min_p > 0 or max_p > 0):
                        modal_p = round((min_p + max_p) / 2.0, 2)

                    if modal_p <= 0:
                        continue

                    # Insert with ON DUPLICATE KEY UPDATE to avoid duplicates
                    cursor.execute(
                        """
                        INSERT INTO daily_prices 
                        (market_id, market_name, district_name, crop_name, variety, arrival_date, min_price, max_price, modal_price, source, raw_payload)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'AGMARKNET_LIVE_API', %s)
                        ON DUPLICATE KEY UPDATE
                            min_price = VALUES(min_price),
                            max_price = VALUES(max_price),
                            modal_price = VALUES(modal_price),
                            variety = VALUES(variety),
                            source = 'AGMARKNET_LIVE_API',
                            raw_payload = VALUES(raw_payload),
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (
                            market_id, official_market_name, district_name, crop_name, variety,
                            arrival_date, min_p, max_p, modal_p, json.dumps(r)
                        )
                    )
                    inserted_count += 1

                msg = f"Successfully synced {len(records)} records from official AGMARKNET. {inserted_count} market prices stored/updated."
                _log_sync("SUCCESS", len(records), inserted_count, msg)
                return {
                    "success": True,
                    "status": "SUCCESS",
                    "message": msg,
                    "records_fetched": len(records),
                    "records_inserted": inserted_count
                }
        finally:
            conn.close()

    except requests.exceptions.Timeout:
        err = "Connection timeout reaching data.gov.in official servers. Government portal took longer than 12 seconds to respond."
        _log_sync("FAILED", 0, 0, err)
        return {
            "success": False,
            "status": "TIMEOUT",
            "message": err,
            "records_fetched": 0,
            "records_inserted": 0
        }
    except requests.exceptions.RequestException as e:
        err = f"Network connection error while connecting to AGMARKNET API: {str(e)}"
        _log_sync("FAILED", 0, 0, err)
        return {
            "success": False,
            "status": "CONNECTION_ERROR",
            "message": err,
            "records_fetched": 0,
            "records_inserted": 0
        }

def _log_sync(status, fetched, inserted, message):
    """Helper to record sync operations in api_sync_logs table."""
    try:
        execute_db(
            """
            INSERT INTO api_sync_logs (source, status, records_fetched, records_inserted, error_message)
            VALUES ('data.gov.in', %s, %s, %s, %s)
            """,
            (status, fetched, inserted, message)
        )
    except Exception as e:
        logger.error(f"Error logging sync: {e}")

def get_last_sync_info():
    """Returns details of the latest API sync attempt."""
    log = query_db(
        "SELECT * FROM api_sync_logs ORDER BY synced_at DESC LIMIT 1",
        one=True
    )
    latest_price = query_db(
        "SELECT MAX(arrival_date) as max_date, MAX(updated_at) as last_updated FROM daily_prices",
        one=True
    )
    return {
        "log": log,
        "latest_arrival_date": latest_price["max_date"] if latest_price else None,
        "last_updated": latest_price["last_updated"] if latest_price else None
    }
