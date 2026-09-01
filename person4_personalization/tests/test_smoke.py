import time
from fastapi.testclient import TestClient
from app import app
from examples.person4_client import Person4Client

client = TestClient(app)
sdk = Person4Client(client_session=client)


# ============================================================
# 1. API SMOKE TESTS FOR ALL CRITICAL PUBLIC ENDPOINTS
# ============================================================

def test_smoke_health_and_readiness():
    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/readiness").status_code == 200
    assert client.get("/api/v1/metrics").status_code == 200


def test_smoke_user_and_portfolio_endpoints():
    user_id = "moderate_001"
    assert client.get(f"/api/v1/users/{user_id}/profile").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/portfolio").status_code == 200


def test_smoke_portfolio_intelligence_endpoints():
    user_id = "moderate_001"
    assert client.get(f"/api/v1/users/{user_id}/portfolio/analysis").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/portfolio/allocation").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/portfolio/concentration").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/portfolio/risk").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/portfolio/risk/advanced").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/portfolio/health").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/portfolio/exposure/RELIANCE.NS?sector=Energy").status_code == 200


def test_smoke_personalization_and_behavior_endpoints():
    user_id = "moderate_001"
    assert client.get(f"/api/v1/users/{user_id}/context/RELIANCE.NS?sector=Energy&market_cap=LARGE&volatility=HIGH").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/behavior").status_code == 200
    assert client.get(f"/api/v1/users/{user_id}/investor-profile").status_code == 200


# ============================================================
# 2. FAILURE RESILIENCE
# ============================================================

def test_failure_resilience_scenarios():
    # Unknown user
    assert client.get("/api/v1/users/non_existent_user/profile").status_code == 404
    assert client.get("/api/v1/users/non_existent_user/portfolio").status_code == 404
    assert client.get("/api/v1/users/non_existent_user/portfolio/analysis").status_code == 404

    # Malformed symbol
    assert client.get("/api/v1/users/moderate_001/context/BAD$$$SYM?sector=Energy").status_code == 422

    # Missing required query param
    assert client.get("/api/v1/users/moderate_001/context/RELIANCE.NS").status_code == 422

    # Invalid pagination parameter
    assert client.get("/api/v1/db/users?skip=-1").status_code == 422


# ============================================================
# 3. PERFORMANCE & LATENCY MEASUREMENT
# ============================================================

def test_performance_latency_check():
    """Measures and reports execution latency for critical operations."""
    endpoints = [
        ("Portfolio Analysis", "/api/v1/users/moderate_001/portfolio/analysis"),
        ("Advanced Risk", "/api/v1/users/moderate_001/portfolio/risk/advanced"),
        ("Personalization Context", "/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy&market_cap=LARGE&volatility=HIGH"),
    ]

    for name, path in endpoints:
        start_time = time.perf_counter()
        resp = client.get(path)
        duration_ms = (time.perf_counter() - start_time) * 1000

        assert resp.status_code == 200
        # Verify response executes within 500ms in local testing
        assert duration_ms < 500.0, f"Endpoint '{name}' exceeded 500ms latency threshold: {duration_ms:.2f}ms"


# ============================================================
# 4. DETERMINISTIC REPEATABILITY TEST
# ============================================================

def test_deterministic_calculation_results():
    """Ensures deterministic financial analytics produce identical output across repeated runs."""
    resp1 = client.get("/api/v1/users/moderate_001/portfolio/analysis").json()
    resp2 = client.get("/api/v1/users/moderate_001/portfolio/analysis").json()

    assert resp1["total_value"] == resp2["total_value"]
    assert resp1["holdings_value"] == resp2["holdings_value"]
    assert resp1["allocation"] == resp2["allocation"]
    assert resp1["concentration"] == resp2["concentration"]
    assert resp1["risk"] == resp2["risk"]
    assert resp1["health"] == resp2["health"]
