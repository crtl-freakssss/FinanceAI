from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


# ============================================================
# HEALTH & READINESS
# ============================================================

def test_root_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "finance-personalization"


def test_v1_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"


def test_v1_readiness():
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "connected"


# ============================================================
# VERSIONED USER & PORTFOLIO ENDPOINTS
# ============================================================

def test_v1_profile_endpoint():
    response = client.get("/api/v1/users/moderate_001/profile")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "moderate_001"
    assert body["risk_tolerance"] == "MODERATE"


def test_v1_portfolio_endpoint():
    response = client.get("/api/v1/users/moderate_001/portfolio")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "moderate_001"
    assert len(body["holdings"]) == 3


def test_v1_unknown_user_returns_404():
    response = client.get("/api/v1/users/unknown_user_999/profile")
    assert response.status_code == 404


# ============================================================
# VERSIONED ANALYTICS & RISK ENDPOINTS
# ============================================================

def test_v1_portfolio_analysis():
    response = client.get("/api/v1/users/moderate_001/portfolio/analysis")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "moderate_001"
    assert "allocation" in body
    assert "concentration" in body
    assert "risk" in body
    assert "health" in body


def test_v1_portfolio_allocation():
    response = client.get("/api/v1/users/moderate_001/portfolio/allocation")
    assert response.status_code == 200
    body = response.json()
    assert "by_symbol" in body
    assert "by_sector" in body


def test_v1_portfolio_concentration():
    response = client.get("/api/v1/users/moderate_001/portfolio/concentration")
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["concentration_score"] <= 100


def test_v1_portfolio_risk_standard_and_advanced():
    std_resp = client.get("/api/v1/users/moderate_001/portfolio/risk")
    assert std_resp.status_code == 200
    assert "risk_score" in std_resp.json()

    adv_resp = client.get("/api/v1/users/moderate_001/portfolio/risk/advanced")
    assert adv_resp.status_code == 200
    adv_body = adv_resp.json()
    assert adv_body["user_id"] == "moderate_001"
    assert "volatility" in adv_body
    assert "drawdown" in adv_body


def test_v1_portfolio_exposure():
    response = client.get("/api/v1/users/moderate_001/portfolio/exposure/RELIANCE.NS?sector=Energy")
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "RELIANCE.NS"
    assert body["sector"] == "Energy"


# ============================================================
# VERSIONED BEHAVIOR & INVESTOR PROFILING
# ============================================================

def test_v1_behavior_endpoint():
    response = client.get("/api/v1/users/moderate_001/behavior")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "moderate_001"
    assert "trading" in body
    assert "holding_period" in body


def test_v1_investor_profile_endpoint():
    response = client.get("/api/v1/users/moderate_001/investor-profile")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "moderate_001"
    assert body["declared_risk_profile"] == "MODERATE"


# ============================================================
# INPUT VALIDATION
# ============================================================

def test_v1_context_validation_invalid_volatility():
    response = client.get("/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy&volatility=EXTREME")
    assert response.status_code == 422


def test_v1_context_validation_invalid_market_cap():
    response = client.get("/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy&market_cap=MEGA")
    assert response.status_code == 422


def test_v1_context_valid_parameters():
    response = client.get("/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy&market_cap=LARGE&volatility=HIGH")
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "RELIANCE.NS"
    assert 0 <= body["risk_score"] <= 100


# ============================================================
# PAGINATION & PERSISTENCE
# ============================================================

def test_v1_pagination_bounds():
    # Invalid limit > 100
    resp_over = client.get("/api/v1/db/users?limit=500")
    assert resp_over.status_code == 422

    # Invalid negative offset
    resp_neg = client.get("/api/v1/db/users?skip=-5")
    assert resp_neg.status_code == 422

    # Valid pagination
    resp_valid = client.get("/api/v1/db/users?skip=0&limit=10")
    assert resp_valid.status_code == 200
    assert isinstance(resp_valid.json(), list)


def test_v1_session_and_log_persistence_with_pagination():
    # Create session
    s_resp = client.post(
        "/api/v1/db/sessions",
        json={
            "user_id": "v1_user_001",
            "symbol": "INFY.NS",
            "analysis_type": "PRODUCTION_TEST",
            "result_data": {"test_metric": 100},
        },
    )
    assert s_resp.status_code == 200
    session_id = s_resp.json()["session_id"]

    # Retrieve sessions paginated
    list_s = client.get("/api/v1/db/users/v1_user_001/sessions?limit=5")
    assert list_s.status_code == 200
    assert any(s["session_id"] == session_id for s in list_s.json())

    # Create log
    l_resp = client.post(
        "/api/v1/db/logs",
        json={
            "user_id": "v1_user_001",
            "message": "Production v1 logging test",
            "level": "INFO",
            "session_id": session_id,
        },
    )
    assert l_resp.status_code == 200

    # Retrieve logs paginated
    list_l = client.get("/api/v1/db/users/v1_user_001/logs?limit=10")
    assert list_l.status_code == 200
    assert len(list_l.json()) >= 1


# ============================================================
# OPENAPI DOCUMENTATION & CORS
# ============================================================

def test_openapi_documentation_accessible():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/readiness" in schema["paths"]
    assert "/api/v1/users/{user_id}/portfolio/risk/advanced" in schema["paths"]


def test_cors_preflight_headers():
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
