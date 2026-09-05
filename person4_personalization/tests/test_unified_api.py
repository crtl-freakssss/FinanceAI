"""
Test Suite for Unified FastAPI Backend (Step 3 Integration).
Validates all versioned endpoints across Person 4 (Personalization/Risk),
Person 2 (Market/News/RAG), and Person 1 (Multi-Agent AI Analysis).
"""

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


# ============================================================
# 1. SYSTEM HEALTH & READINESS TESTS
# ============================================================

def test_root_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_v1_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_v1_readiness():
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


# ============================================================
# 2. PERSON 4 PERSONALIZATION & PORTFOLIO ENDPOINTS
# ============================================================

def test_p4_user_profile_endpoint():
    response = client.get("/api/v1/users/moderate_001/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "moderate_001"
    assert "risk_tolerance" in data
    assert "investment_horizon" in data


def test_p4_user_portfolio_endpoint():
    response = client.get("/api/v1/users/moderate_001/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "moderate_001"
    assert "holdings" in data
    assert "cash" in data


def test_p4_portfolio_analysis_endpoints():
    endpoints = [
        "/api/v1/users/moderate_001/portfolio/analysis",
        "/api/v1/users/moderate_001/portfolio/allocation",
        "/api/v1/users/moderate_001/portfolio/concentration",
        "/api/v1/users/moderate_001/portfolio/risk",
        "/api/v1/users/moderate_001/portfolio/health",
        "/api/v1/users/moderate_001/portfolio/exposure/RELIANCE.NS",
    ]
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200, f"Endpoint {ep} failed with status {resp.status_code}"


def test_p4_advanced_risk_endpoint():
    response = client.get("/api/v1/users/moderate_001/portfolio/risk/advanced")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "moderate_001"
    assert "risk_score" in data
    assert "risk_level" in data
    assert "value_at_risk" in data or "volatility" in data



def test_p4_personalization_context_endpoint():
    response = client.get("/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "moderate_001"
    assert "suitability" in data


# ============================================================
# 3. PERSON 2 MARKET, INDICATORS, NEWS & RAG ENDPOINTS
# ============================================================

def test_p2_market_quote_endpoint():
    response = client.get("/api/v1/market/RELIANCE.NS")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "RELIANCE.NS"
    assert "price" in data
    assert data["price"] > 0


def test_p2_market_history_endpoint():
    response = client.get("/api/v1/market/TCS.NS/history?period=1mo")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "TCS.NS"
    assert "history" in data
    assert len(data["history"]) > 0


def test_p2_market_indicators_endpoint():
    response = client.get("/api/v1/market/INFY.NS/indicators?period=3mo")
    assert response.status_code == 200
    data = response.json()
    assert "rsi" in data
    assert "macd" in data
    assert "volatility" in data


def test_p2_news_endpoint():
    response = client.get("/api/v1/news/HDFCBANK.NS")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "sentiment" in data


def test_p2_rag_query_post_endpoint():
    payload = {
        "query": "What are Reliance revenue growth and earnings?",
        "symbol": "RELIANCE.NS",
        "top_k": 3,
    }
    response = client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_p2_rag_query_get_endpoint():
    response = client.get("/api/v1/rag/query?query=TCS+financial+results&top_k=2")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


# ============================================================
# 4. PERSON 1 MULTI-AGENT AI ANALYSIS ENDPOINT
# ============================================================

def test_p1_ai_analyze_endpoint_success():
    payload = {
        "user_id": "moderate_001",
        "symbol": "RELIANCE.NS",
        "analysis_type": "full",
        "include_rag": True,
        "include_news": True,
    }
    response = client.post("/api/v1/ai/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == "moderate_001"
    assert data["normalized_symbol"] == "RELIANCE.NS"
    assert data["signal"] in ["BUY", "HOLD", "SELL", "AVOID"]
    assert "confidence" in data
    assert "verdict" in data
    assert "key_drivers" in data
    assert "risk_assessment" in data
    assert "metrics" in data
    assert data["metrics"]["parallel_execution"] is True


def test_p1_ai_analyze_all_demo_archetypes():
    users = ["moderate_001", "conservative_001", "aggressive_001"]
    for user_id in users:
        payload = {"user_id": user_id, "symbol": "TCS"}
        response = client.post("/api/v1/ai/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["signal"] in ["BUY", "HOLD", "SELL", "AVOID"]


# ============================================================
# 5. ERROR HANDLING & VALIDATION TESTS
# ============================================================

def test_ai_analyze_missing_user_returns_404():
    payload = {"user_id": "non_existent_user_999", "symbol": "RELIANCE.NS"}
    response = client.post("/api/v1/ai/analyze", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_ai_analyze_empty_symbol_returns_422():
    payload = {"user_id": "moderate_001", "symbol": "   "}
    response = client.post("/api/v1/ai/analyze", json=payload)
    assert response.status_code == 422


def test_ai_analyze_malformed_request_returns_422():
    payload = {"invalid_key": 123}
    response = client.post("/api/v1/ai/analyze", json=payload)
    assert response.status_code == 422


def test_degraded_market_behavior():
    response = client.get("/api/v1/market/UNKNOWN_SYM_123")
    assert response.status_code == 200
    data = response.json()
    assert "source" in data


# ============================================================
# 6. OPENAPI SPECIFICATION AVAILABILITY
# ============================================================

def test_openapi_json_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/ai/analyze" in schema["paths"]
    assert "/api/v1/market/{symbol}" in schema["paths"]
    assert "/api/v1/rag/query" in schema["paths"]
    assert "/api/v1/users/{user_id}/profile" in schema["paths"]


def test_swagger_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200


def test_terminal_dashboard_ui_available():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "SI Terminal" in response.text
    assert "api.js" in response.text


def test_terminal_alias_route_available():
    response = client.get("/terminal")
    assert response.status_code == 200
    assert "SI Terminal" in response.text


def test_static_api_js_available():
    response = client.get("/ui/api.js")
    assert response.status_code == 200
    assert "StICApiClient" in response.text

