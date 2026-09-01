import pytest
from market.market_data import get_market_data, normalize_symbol
from market.price_history import get_price_history, _generate_deterministic_history
from market.indicators import get_indicators
from market.cache import get_cache, set_cache

# 1. Market Data Tests
def test_valid_demo_symbols():
    for sym in ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS"]:
        data = get_market_data(sym)
        assert data is not None
        assert "symbol" in data
        assert data["symbol"] == sym
        assert "price" in data
        assert "source" in data
        assert data["source"] in ["live", "cache", "mock"]
        assert "timestamp" in data

def test_symbol_normalization():
    assert normalize_symbol("reliance") == "RELIANCE.NS"
    assert normalize_symbol("TCS") == "TCS.NS"
    assert normalize_symbol("INFOSYS") == "INFY.NS"
    assert normalize_symbol("hdfcbank.ns") == "HDFCBANK.NS"
    assert normalize_symbol("ITC") == "ITC.NS"

def test_unsupported_symbol():
    data = get_market_data("COMPLETELY_UNKNOWN_XYZ")
    assert data is not None
    assert data["symbol"] == "COMPLETELY_UNKNOWN_XYZ.NS"
    assert data["source"] in ["mock", "live", "cache"]

def test_market_cache_mechanism():
    test_key = "test_cache_quote"
    test_payload = {"symbol": "TEST.NS", "price": 1234.56, "source": "cache"}
    set_cache(test_key, test_payload)
    
    cached = get_cache(test_key, max_age_seconds=60)
    assert cached is not None
    assert cached["price"] == 1234.56

# 2. Historical Price Tests
def test_price_history_periods():
    for period in ["1mo", "3mo", "6mo", "1y"]:
        data = get_price_history("RELIANCE.NS", period=period)
        assert data is not None
        assert "history" in data
        assert len(data["history"]) > 0
        assert data["period"] == period
        first_row = data["history"][0]
        assert "Date" in first_row
        assert "Open" in first_row
        assert "High" in first_row
        assert "Low" in first_row
        assert "Close" in first_row
        assert "Volume" in first_row

def test_deterministic_history_generator():
    hist = _generate_deterministic_history("TCS.NS", "3mo")
    assert hist["symbol"] == "TCS.NS"
    assert hist["period"] == "3mo"
    assert hist["count"] == 90
    assert len(hist["history"]) == 90

# 3. Indicators Tests
def test_indicators_full_calculation():
    hist_data = get_price_history("TCS.NS", "3mo")
    ind = get_indicators("TCS.NS", hist_data)
    
    assert ind["symbol"] == "TCS.NS"
    assert ind["status"] == "Calculated"
    assert ind["ema9"] is not None
    assert ind["ema21"] is not None
    assert ind["rsi"] is not None
    assert 0 <= ind["rsi"] <= 100
    assert ind["macd"] is not None
    assert ind["volatility"] is not None
    assert ind["momentum"] is not None
    assert ind["percentage_price_change"] is not None

def test_indicators_insufficient_data():
    empty_res = get_indicators("EMPTY.NS", {"history": []})
    assert empty_res["status"] == "Insufficient data"
    assert empty_res["ema9"] is None
    assert empty_res["rsi"] is None

def test_indicators_single_point():
    single_res = get_indicators("ONE.NS", {"history": [{"Date": "2025-01-01", "Close": 100, "Volume": 10}]})
    assert single_res["status"] == "Insufficient data"
    assert single_res["macd"] is None
