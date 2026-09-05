try:
    import yfinance as yf
except ImportError:
    yf = None

import json
import os
import datetime
from .cache import get_cache, set_cache


MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "mock_data", "market.json")

SUPPORTED_DEMO_SYMBOLS = {
    "RELIANCE": "RELIANCE.NS",
    "RELIANCE.NS": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "TCS.NS": "TCS.NS",
    "INFY": "INFY.NS",
    "INFY.NS": "INFY.NS",
    "INFOSYS": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "HDFCBANK.NS": "HDFCBANK.NS",
    "ITC": "ITC.NS",
    "ITC.NS": "ITC.NS"
}

def normalize_symbol(symbol: str) -> str:
    sym = symbol.strip().upper()
    return SUPPORTED_DEMO_SYMBOLS.get(sym, sym if "." in sym else f"{sym}.NS")

def get_market_data(symbol: str) -> dict:
    """
    Retrieves current market data for a given symbol.
    
    Fallback chain:
    1. Live yfinance API
    2. Local Cache (TTL 1 hour / 24 hours fallback)
    3. Mock Data (deterministic demo data)
    
    Source is clearly identified as 'live', 'cache', or 'mock'.
    """
    normalized = normalize_symbol(symbol)
    cache_key = f"market_quote_{normalized}"
    
    # 1. Attempt Live yfinance fetch
    try:
        ticker = yf.Ticker(normalized)
        # fast_info is quicker and more reliable than .info in recent yfinance
        fast = getattr(ticker, "fast_info", None)
        curr_price = None
        prev_close = None
        open_price = None
        high_price = None
        low_price = None
        volume = None
        currency = "INR"

        if fast:
            try:
                curr_price = fast.last_price
                prev_close = fast.previous_close
                open_price = fast.open
                high_price = fast.day_high
                low_price = fast.day_low
                volume = fast.last_volume
                currency = getattr(fast, "currency", "INR") or "INR"
            except Exception:
                pass

        if not curr_price:
            info = ticker.info
            if info:
                curr_price = info.get("currentPrice") or info.get("regularMarketPrice")
                prev_close = info.get("previousClose")
                open_price = info.get("open") or info.get("regularMarketOpen")
                high_price = info.get("dayHigh") or info.get("regularMarketDayHigh")
                low_price = info.get("dayLow") or info.get("regularMarketDayLow")
                volume = info.get("volume") or info.get("regularMarketVolume")
                currency = info.get("currency", "INR")

        if curr_price is not None and not (isinstance(curr_price, float) and (curr_price != curr_price)): # not NaN
            prev = prev_close if prev_close else curr_price
            change = round(curr_price - prev, 2)
            change_pct = round((change / prev) * 100.0, 2) if prev else 0.0
            
            result = {
                "symbol": normalized,
                "price": round(float(curr_price), 2),
                "open": round(float(open_price), 2) if open_price else None,
                "high": round(float(high_price), 2) if high_price else None,
                "low": round(float(low_price), 2) if low_price else None,
                "previous_close": round(float(prev), 2),
                "change": change,
                "change_percentage": change_pct,
                "volume": int(volume) if volume else 0,
                "currency": currency,
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "live",
                "status": "Live data successfully retrieved"
            }
            set_cache(cache_key, result)
            return result
    except Exception as e:
        # Fall through to cache/mock
        pass

    # 2. Attempt Cache fetch
    cached = get_cache(cache_key, max_age_seconds=86400)
    if cached:
        cached_copy = dict(cached)
        cached_copy["source"] = "cache"
        cached_copy["status"] = "Live market data unavailable. Using cached data."
        return cached_copy

    # 3. Attempt Mock Data fetch
    if os.path.exists(MOCK_DATA_PATH):
        try:
            with open(MOCK_DATA_PATH, 'r', encoding='utf-8') as f:
                mock_db = json.load(f)
            if normalized in mock_db:
                item = dict(mock_db[normalized])
                item["source"] = "mock"
                item["status"] = "Live market data unavailable. Using demo mock data."
                item["timestamp"] = datetime.datetime.now().isoformat()
                return item
        except Exception:
            pass

    # Generic fallback if symbol is completely unknown
    return {
        "symbol": normalized,
        "price": 0.0,
        "open": None,
        "high": None,
        "low": None,
        "previous_close": 0.0,
        "change": 0.0,
        "change_percentage": 0.0,
        "volume": 0,
        "currency": "INR",
        "timestamp": datetime.datetime.now().isoformat(),
        "source": "mock",
        "status": f"Live market data unavailable for {normalized}. No demo record found."
    }
