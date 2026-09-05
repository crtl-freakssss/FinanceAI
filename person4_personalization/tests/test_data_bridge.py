"""
Test Suite for Data Bridge (Person 1 + Person 2 + Person 4 Integration).
Validates symbol normalization, indicator normalization, RAG retrieval, profile extraction,
degraded mode handling, and unified AI input payload construction.
"""

import pytest
from data_bridge import (
    FinancialDataBridge,
    data_bridge,
    normalize_symbol_pair,
    UserNotFoundError,
    SymbolNotFoundError,
    UnifiedAIInput,
    MarketDataInput,
    NewsDataInput,
    FundamentalDataInput,
    UserProfileInput,
)


# ============================================================
# 1. SYMBOL NORMALIZATION TESTS
# ============================================================

def test_symbol_normalization_indian_equities():
    req, norm = normalize_symbol_pair("RELIANCE")
    assert req == "RELIANCE"
    assert norm == "RELIANCE.NS"

    req, norm = normalize_symbol_pair("tcs")
    assert req == "TCS"
    assert norm == "TCS.NS"

    req, norm = normalize_symbol_pair("HDFCBANK.NS")
    assert req == "HDFCBANK.NS"
    assert norm == "HDFCBANK.NS"


def test_symbol_normalization_us_equities():
    req, norm = normalize_symbol_pair("AAPL")
    assert req == "AAPL"
    assert norm == "AAPL"  # Preserves US ticker without appending .NS

    req, norm = normalize_symbol_pair("nvda")
    assert req == "NVDA"
    assert norm == "NVDA"


def test_symbol_normalization_empty_raises():
    with pytest.raises(SymbolNotFoundError):
        normalize_symbol_pair("")

    with pytest.raises(SymbolNotFoundError):
        normalize_symbol_pair("   ")


# ============================================================
# 2. PERSON 4 DATA EXTRACTION TESTS
# ============================================================

def test_get_user_profile_data_existing_user():
    bridge = FinancialDataBridge()
    profile_data = bridge.get_user_profile_data("moderate_001", symbol="RELIANCE.NS")

    assert isinstance(profile_data, UserProfileInput)
    assert profile_data.user_id == "moderate_001"
    assert profile_data.risk_tolerance in ["conservative", "moderate", "aggressive"]
    assert profile_data.total_portfolio_value > 0
    assert profile_data.portfolio_exposure >= 0.0
    assert profile_data.investment_horizon in ["short_term", "medium_term", "long_term"]


def test_get_user_profile_data_missing_user():
    bridge = FinancialDataBridge()
    with pytest.raises(UserNotFoundError):
        bridge.get_user_profile_data("non_existent_user_999")


def test_get_personalization_context():
    bridge = FinancialDataBridge()
    context = bridge.get_personalization_context(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        sector="Energy",
        market_cap="LARGE",
        volatility="MEDIUM",
    )
    assert context.user_id == "moderate_001"
    assert context.symbol == "RELIANCE.NS"
    assert str(context.suitability).upper() in ["SUITABLE", "CAUTION", "UNSUITABLE"]
    assert context.suitability_score >= 0.0


# ============================================================
# 3. PERSON 2 MARKET, NEWS & RAG RETRIEVAL TESTS
# ============================================================

def test_get_market_data_for_agent():
    bridge = FinancialDataBridge()
    market = bridge.get_market_data_for_agent("RELIANCE.NS")

    assert isinstance(market, MarketDataInput)
    assert market.price >= 0.0
    assert 0.0 <= market.rsi <= 100.0
    assert market.volatility >= 0.0
    assert isinstance(market.available_indicators, list)


def test_indicator_normalization_non_fabricated():
    bridge = FinancialDataBridge()
    market = bridge.get_market_data_for_agent("RELIANCE.NS")

    # If EMA20 is available, it must be a positive float; if not, it should be None or matched in available_indicators
    if market.ema20 is not None:
        assert market.ema20 > 0.0
        assert "ema20" in market.available_indicators
    assert 0.0 <= market.rsi <= 100.0


def test_get_news_data_for_agent():
    bridge = FinancialDataBridge()
    news = bridge.get_news_data_for_agent("TCS.NS")

    assert isinstance(news, NewsDataInput)
    assert 0.0 <= news.sentiment_score <= 1.0
    assert isinstance(news.headlines, list)


def test_get_fundamental_data_for_agent():
    bridge = FinancialDataBridge()
    fundamentals = bridge.get_fundamental_data_for_agent("INFY.NS")

    assert isinstance(fundamentals, FundamentalDataInput)
    assert fundamentals.pe_ratio > 0.0
    assert fundamentals.rag_summary != ""
    assert isinstance(fundamentals.sources, list)


def test_rag_retrieval_and_citations():
    bridge = FinancialDataBridge()
    fundamentals = bridge.get_fundamental_data_for_agent("RELIANCE.NS")

    assert fundamentals.status == "ok"
    assert len(fundamentals.sources) > 0
    assert len(fundamentals.rag_summary) > 10


# ============================================================
# 4. DEGRADED MODE & RESILIENCE TESTS
# ============================================================

def test_degraded_mode_unknown_symbol():
    bridge = FinancialDataBridge()
    market = bridge.get_market_data_for_agent("UNKNOWN_SYMBOL_XYZ")

    assert isinstance(market, MarketDataInput)
    assert 0.0 <= market.rsi <= 100.0
    assert market.source in ["mock", "fallback", "unknown"]
    assert "unavailable" in market.status.lower() or "demo" in market.status.lower() or market.status == "ok"



def test_degraded_mode_empty_news():
    bridge = FinancialDataBridge()
    news = bridge.get_news_data_for_agent("UNKNOWN_SYMBOL_XYZ")

    assert isinstance(news, NewsDataInput)
    assert 0.0 <= news.sentiment_score <= 1.0


# ============================================================
# 5. UNIFIED AI INPUT PAYLOAD BUILDER TESTS
# ============================================================

def test_build_ai_analysis_input_complete_structure():
    bridge = FinancialDataBridge()
    ai_input = bridge.build_ai_analysis_input(user_id="moderate_001", symbol="TCS")

    assert isinstance(ai_input, UnifiedAIInput)
    assert ai_input.symbol == "TCS"
    assert ai_input.normalized_symbol == "TCS.NS"

    # Verify market_data fields expected by Person 1 TechnicalAgent
    m = ai_input.market_data
    assert "price" in m
    assert "rsi" in m
    assert "ema20" in m
    assert "ema50" in m
    assert "macd" in m
    assert "volume_change" in m
    assert "momentum" in m
    assert "volatility" in m

    # Verify news_data fields expected by Person 1 SentimentAgent
    n = ai_input.news_data
    assert "sentiment_score" in n
    assert "positive_news" in n
    assert "negative_news" in n
    assert "headlines" in n

    # Verify fundamental_data fields expected by Person 1 FundamentalAgent
    f = ai_input.fundamental_data
    assert "revenue_growth" in f
    assert "profit_growth" in f
    assert "pe_ratio" in f
    assert "rag_summary" in f
    assert "sources" in f

    # Verify user_profile fields expected by Person 1 RiskAgent
    p = ai_input.user_profile
    assert "risk_tolerance" in p
    assert "portfolio_exposure" in p
    assert "investment_horizon" in p


def test_build_ai_analysis_input_all_demo_users():
    bridge = FinancialDataBridge()
    for user_id in ["moderate_001", "conservative_001", "aggressive_001"]:
        ai_input = bridge.build_ai_analysis_input(user_id=user_id, symbol="RELIANCE.NS")
        assert ai_input.user_profile["risk_tolerance"] in ["conservative", "moderate", "aggressive"]
        assert ai_input.meta["user_id"] == user_id
        assert ai_input.market_data["price"] > 0
