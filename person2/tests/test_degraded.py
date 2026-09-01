import pytest
from market.market_data import get_market_data
from market.price_history import get_price_history
from news.news_fetcher import get_news
from rag.retriever import retrieve
from filings.filing_fetcher import get_filings

def test_degraded_market_unknown_ticker():
    res = get_market_data("NONEXISTENT_TICKER_99999")
    assert res is not None
    assert res["source"] == "mock"
    assert "No demo record found" in res.get("status", "") or res.get("price") == 0.0

def test_degraded_history_fallback():
    hist = get_price_history("UNKNOWN_STOCK_XYZ", period="1mo")
    assert hist is not None
    assert hist["source"] == "mock"
    assert len(hist["history"]) > 0

def test_degraded_news_fallback():
    news_res = get_news("RANDOM_CORP_ABC")
    assert news_res is not None
    assert news_res["source"] == "mock"
    assert "demo news" in news_res.get("status", "").lower()

def test_degraded_rag_no_query_match():
    # If the collection is queried for something without match or empty, handled gracefully
    res = retrieve("Martian space rover agricultural yields in year 3000", top_k=2)
    assert res is not None
    assert "results" in res
    assert "query" in res

def test_local_filings_availability():
    filings = get_filings("RELIANCE.NS")
    assert filings is not None
    assert filings["source"] == "local_corpus"
    assert filings["count"] >= 1
