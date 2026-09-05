try:
    import yfinance as yf
except ImportError:
    yf = None

import pandas as pd
import json
import os
import datetime
from .cache import get_cache, set_cache


MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "mock_data", "market.json")

SUPPORTED_PERIODS = ["1mo", "3mo", "6mo", "1y"]

def get_price_history(symbol: str, period: str = "1mo") -> dict:
    """
    Retrieves historical OHLCV data for a given symbol and period.
    Supported periods: 1mo, 3mo, 6mo, 1y.
    
    Fallback chain:
    1. Live yfinance history
    2. Cached history
    3. Deterministic mock history from mock_data/market.json or dynamic generator.
    """
    period = period if period in SUPPORTED_PERIODS else "1mo"
    sym = symbol.strip().upper()
    normalized = sym if "." in sym else f"{sym}.NS"
    cache_key = f"price_history_{normalized}_{period}"

    # 1. Attempt Live yfinance fetch
    try:
        ticker = yf.Ticker(normalized)
        df = ticker.history(period=period)
        if df is not None and not df.empty and len(df) > 0:
            df.reset_index(inplace=True)
            # Find date column
            date_col = 'Date' if 'Date' in df.columns else df.columns[0]
            df['FormattedDate'] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
            
            records = []
            for _, row in df.iterrows():
                records.append({
                    "Date": str(row['FormattedDate']),
                    "Open": round(float(row.get('Open', 0.0)), 2),
                    "High": round(float(row.get('High', 0.0)), 2),
                    "Low": round(float(row.get('Low', 0.0)), 2),
                    "Close": round(float(row.get('Close', 0.0)), 2),
                    "Volume": int(row.get('Volume', 0))
                })
            
            result = {
                "symbol": normalized,
                "period": period,
                "count": len(records),
                "history": records,
                "source": "live",
                "status": "Live history successfully retrieved"
            }
            set_cache(cache_key, result)
            return result
    except Exception:
        pass

    # 2. Attempt Cache fetch
    cached = get_cache(cache_key, max_age_seconds=86400)
    if cached:
        cached_copy = dict(cached)
        cached_copy["source"] = "cache"
        cached_copy["status"] = "Live history unavailable. Using cached history."
        return cached_copy

    # 3. Attempt Mock Data from file
    if os.path.exists(MOCK_DATA_PATH):
        try:
            with open(MOCK_DATA_PATH, 'r', encoding='utf-8') as f:
                mock_db = json.load(f)
            if normalized in mock_db and "history" in mock_db[normalized]:
                full_history = mock_db[normalized]["history"]
                slice_len = 30 if period == "1mo" else (60 if period == "3mo" else (120 if period == "6mo" else 250))
                selected_history = full_history[-slice_len:] if len(full_history) >= slice_len else full_history
                return {
                    "symbol": normalized,
                    "period": period,
                    "count": len(selected_history),
                    "history": selected_history,
                    "source": "mock",
                    "status": "Live history unavailable. Using demo mock history."
                }
        except Exception:
            pass

    # 4. Deterministic fallback generator
    return _generate_deterministic_history(normalized, period)

def _generate_deterministic_history(symbol: str, period: str) -> dict:
    days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 252}
    total_days = days_map.get(period, 30)
    
    # Deterministic base price based on hash of symbol
    base_price = 1000.0 + (abs(hash(symbol)) % 2500)
    history = []
    today = datetime.date.today()
    
    current_p = base_price
    for i in range(total_days):
        d = (today - datetime.timedelta(days=total_days - i - 1)).strftime('%Y-%m-%d')
        # Deterministic variation
        var = ((i * 17) % 31) - 15
        current_p = round(max(10.0, current_p + (var * 0.5)), 2)
        history.append({
            "Date": d,
            "Open": round(current_p - 5.0, 2),
            "High": round(current_p + 10.0, 2),
            "Low": round(current_p - 10.0, 2),
            "Close": current_p,
            "Volume": 1000000 + ((i * 50000) % 1500000)
        })
        
    return {
        "symbol": symbol,
        "period": period,
        "count": len(history),
        "history": history,
        "source": "mock",
        "status": "Live history unavailable. Generated deterministic demo history."
    }
