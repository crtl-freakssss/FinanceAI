import pytest
from fastapi.testclient import TestClient
from app import app
from examples.person4_client import Person4Client

client = TestClient(app)
sdk = Person4Client(client_session=client)


# ============================================================
# 1. OPENAPI SPECIFICATION CONTAINS ALL V1 PUBLIC ENDPOINTS
# ============================================================

def test_openapi_contains_all_public_v1_endpoints():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})

    expected_endpoints = [
        "/api/v1/health",
        "/api/v1/readiness",
        "/api/v1/metrics",
        "/api/v1/users/{user_id}/profile",
        "/api/v1/users/{user_id}/portfolio",
        "/api/v1/users/{user_id}/context/{symbol}",
        "/api/v1/users/{user_id}/portfolio/analysis",
        "/api/v1/users/{user_id}/portfolio/allocation",
        "/api/v1/users/{user_id}/portfolio/concentration",
        "/api/v1/users/{user_id}/portfolio/risk",
        "/api/v1/users/{user_id}/portfolio/risk/advanced",
        "/api/v1/users/{user_id}/portfolio/health",
        "/api/v1/users/{user_id}/portfolio/exposure/{symbol}",
        "/api/v1/users/{user_id}/behavior",
        "/api/v1/users/{user_id}/investor-profile",
        "/api/v1/db/users",
        "/api/v1/db/sessions",
        "/api/v1/db/logs",
    ]

    for endpoint in expected_endpoints:
        assert endpoint in paths, f"Endpoint '{endpoint}' missing from OpenAPI spec"


# ============================================================
# 2. PUBLIC API CONTRACT VIA SDK (PERSON 1, 2, 3 INTERFACE)
# ============================================================

def test_sdk_health_and_readiness():
    health = sdk.get_health()
    assert health["status"] == "ok"
    assert health["version"] == "1.0.0"

    readiness = sdk.get_readiness()
    assert readiness["status"] == "ready"
    assert readiness["database"] == "connected"

    metrics = sdk.get_metrics()
    assert metrics["status"] == "ok"
    assert "metrics" in metrics


def test_sdk_person1_personalization_context():
    """Person 1 recommendation synthesis contract test."""
    context = sdk.get_personalization_context(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        sector="Energy",
        market_cap="LARGE",
        volatility="HIGH",
    )
    assert context["user_id"] == "moderate_001"
    assert context["symbol"] == "RELIANCE.NS"
    assert context["sector"] == "Energy"
    assert "risk_score" in context
    assert "risk_level" in context
    assert "suitability_score" in context
    assert "suitability" in context
    assert "reasons" in context
    assert "warnings" in context
    assert "constraint_breaches" in context


def test_sdk_person2_advanced_risk():
    """Person 2 quantitative risk contract test."""
    adv_risk = sdk.get_advanced_risk("moderate_001")
    assert adv_risk["user_id"] == "moderate_001"
    assert "risk_score" in adv_risk
    assert "risk_level" in adv_risk
    assert "volatility" in adv_risk
    assert "drawdown" in adv_risk
    assert "sector_risk" in adv_risk
    assert "liquidity" in adv_risk


def test_sdk_person3_portfolio_analytics():
    """Person 3 frontend portfolio analysis contract test."""
    analysis = sdk.get_portfolio_analysis("moderate_001")
    assert analysis["user_id"] == "moderate_001"
    assert analysis["total_value"] > 0
    assert "allocation" in analysis
    assert "concentration" in analysis
    assert "risk" in analysis
    assert "health" in analysis

    alloc = sdk.get_portfolio_allocation("moderate_001")
    assert len(alloc["by_symbol"]) > 0
    assert len(alloc["by_sector"]) > 0

    conc = sdk.get_portfolio_concentration("moderate_001")
    assert "concentration_score" in conc

    health = sdk.get_portfolio_health("moderate_001")
    assert "health_score" in health
    assert "status" in health

    exposure = sdk.get_exposure("moderate_001", "RELIANCE.NS", sector="Energy")
    assert exposure["symbol"] == "RELIANCE.NS"


def test_sdk_person3_behavioral_and_investor_profile():
    """Person 3 behavioral profile contract test."""
    behavior = sdk.get_behavior("moderate_001")
    assert behavior["user_id"] == "moderate_001"
    assert "trading" in behavior
    assert "holding_period" in behavior
    assert "performance" in behavior

    inv_profile = sdk.get_investor_profile("moderate_001")
    assert inv_profile["user_id"] == "moderate_001"
    assert inv_profile["declared_risk_profile"] == "MODERATE"
    assert "alignment" in inv_profile
    assert "profile_confidence" in inv_profile


# ============================================================
# 3. STABLE ERROR HANDLING & CORRELATION HEADERS
# ============================================================

def test_missing_user_returns_404_with_correlation_headers():
    response = client.get("/api/v1/users/non_existent_9999/profile")
    assert response.status_code == 404
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_missing_portfolio_returns_404():
    response = client.get("/api/v1/users/non_existent_9999/portfolio")
    assert response.status_code == 404


def test_invalid_query_returns_422_with_validation_errors():
    response = client.get("/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy&volatility=INVALID_VOL")
    assert response.status_code == 422
    assert "detail" in response.json()
