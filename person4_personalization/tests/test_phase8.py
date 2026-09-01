import math
import pytest
from fastapi.testclient import TestClient
from app import app
from security.config import security_config
from security.rate_limiter import rate_limiter
from security.validation import (
    validate_symbol,
    validate_user_id,
    is_valid_finite_number,
    sanitize_numeric,
)
from portfolio.analytics import (
    calculate_allocation,
    calculate_concentration,
    calculate_portfolio_risk,
    calculate_portfolio_health,
)

client = TestClient(app)


# ============================================================
# 1. INPUT VALIDATION & IDENTIFIER SAFETY
# ============================================================

def test_valid_and_invalid_user_ids():
    assert validate_user_id("moderate_001") is True
    assert validate_user_id("user-123_abc") is True
    assert validate_user_id("../etc/passwd") is False
    assert validate_user_id("user/with/slashes") is False
    assert validate_user_id("") is False


def test_valid_and_invalid_symbols():
    assert validate_symbol("RELIANCE.NS") is True
    assert validate_symbol("TCS.NS") is True
    assert validate_symbol("AAPL") is True
    assert validate_symbol("../../../secret") is False
    assert validate_symbol("SYMBOL$$$#") is False
    assert validate_symbol("") is False


def test_api_rejects_malformed_symbol():
    response = client.get("/api/v1/users/moderate_001/context/INVALID$$$SYMBOL?sector=Energy")
    assert response.status_code == 422


# ============================================================
# 2. NUMERIC & FINANCIAL VALIDATION (NaN, Infinity, Negative)
# ============================================================

def test_finite_number_validation():
    assert is_valid_finite_number(100.5) is True
    assert is_valid_finite_number(0.0) is True
    assert is_valid_finite_number(-50.0) is True
    assert is_valid_finite_number(float("nan")) is False
    assert is_valid_finite_number(float("inf")) is False
    assert is_valid_finite_number(float("-inf")) is False
    assert is_valid_finite_number("invalid_string") is False


def test_sanitize_numeric_helper():
    assert sanitize_numeric(50.0, default=0.0) == 50.0
    assert sanitize_numeric(float("nan"), default=10.0) == 10.0
    assert sanitize_numeric(float("inf"), default=0.0) == 0.0
    assert sanitize_numeric(-10.0, min_val=0.0) == 0.0
    assert sanitize_numeric(150.0, max_val=100.0) == 100.0


def test_api_rejects_negative_portfolio_values():
    response = client.post(
        "/api/v1/db/users/user_sec_001/portfolio",
        json={
            "total_value": -5000.0,
            "cash": -100.0,
            "holdings": [],
        },
    )
    assert response.status_code == 422


def test_api_rejects_invalid_holding_shares():
    response = client.post(
        "/api/v1/db/users/user_sec_002/portfolio",
        json={
            "total_value": 50000.0,
            "cash": 1000.0,
            "holdings": [
                {"symbol": "TCS.NS", "shares": -10, "price": 3500.0},
            ],
        },
    )
    assert response.status_code == 422


# ============================================================
# 3. EMPTY & ZERO-VALUE PORTFOLIO SAFETY
# ============================================================

def test_empty_portfolio_does_not_crash_analytics():
    empty_portfolio = {"total_value": 0.0, "cash": 0.0, "holdings": []}
    
    alloc = calculate_allocation(empty_portfolio)
    assert alloc.by_symbol == []
    assert alloc.by_sector == []

    conc = calculate_concentration(empty_portfolio)
    assert conc.concentration_score == 0.0

    risk = calculate_portfolio_risk(empty_portfolio, conc)
    assert risk.risk_score >= 0.0

    health = calculate_portfolio_health(empty_portfolio, conc, risk)
    assert health.health_score >= 0.0


def test_financial_calculations_never_produce_nan_or_inf():
    zero_portfolio = {
        "total_value": 0.0,
        "cash": 0.0,
        "holdings": [
            {"symbol": "ZERO.NS", "shares": 0.0, "price": 0.0, "value": 0.0, "sector": "Tech"}
        ],
    }
    alloc = calculate_allocation(zero_portfolio)
    for item in alloc.by_symbol:
        assert not math.isnan(item.percentage)
        assert not math.isinf(item.percentage)


# ============================================================
# 4. SECURITY HEADERS & CORS CONFIGURATION
# ============================================================

def test_security_headers_present():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert response.headers.get("Content-Security-Policy") == "default-src 'self'"
    assert "geolocation=()" in response.headers.get("Permissions-Policy", "")


def test_swagger_docs_csp_headers():
    response = client.get("/docs")
    assert response.status_code == 200
    csp = response.headers.get("Content-Security-Policy", "")
    assert "cdn.jsdelivr.net" in csp
    assert "fastapi.tiangolo.com" in csp
    assert "default-src 'self'" in csp



def test_cors_configuration_is_safe():
    assert "*" not in security_config.ALLOWED_ORIGINS
    for origin in security_config.ALLOWED_ORIGINS:
        assert origin.startswith("http://") or origin.startswith("https://")


# ============================================================
# 5. REQUEST SIZE & RATE LIMITING PROTECTION
# ============================================================

def test_oversized_payload_rejected():
    # Attempt to send payload larger than configured MAX_REQUEST_SIZE
    large_payload = "A" * (security_config.MAX_REQUEST_SIZE + 1024)
    response = client.post(
        "/api/v1/db/users",
        content=large_payload,
        headers={"Content-Type": "application/json", "Content-Length": str(len(large_payload))},
    )
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"]


def test_rate_limiter_blocks_excessive_requests():
    rate_limiter.reset()
    client_ip = "192.168.1.100"
    
    # Send requests up to the limit
    for _ in range(rate_limiter.limit):
        allowed, _ = rate_limiter.is_allowed(client_ip)
        assert allowed is True

    # Next request must be rejected
    allowed, retry_after = rate_limiter.is_allowed(client_ip)
    assert allowed is False
    assert retry_after > 0

    # Cleanup rate limiter for other tests
    rate_limiter.reset()


# ============================================================
# 6. SECRETS & ERROR RESPONSE SANITIZATION
# ============================================================

def test_error_response_does_not_leak_stack_traces_or_paths():
    response = client.get("/api/v1/users/non_existent_user_xyz/profile")
    assert response.status_code == 404
    body = str(response.json())
    assert "Traceback" not in body
    assert "C:\\" not in body
    assert "/home/" not in body
    assert "password" not in body.lower()
    assert "secret" not in body.lower()


def test_health_and_readiness_still_work():
    h = client.get("/health")
    assert h.status_code == 200
    assert h.json()["status"] == "ok"

    v1_h = client.get("/api/v1/health")
    assert v1_h.status_code == 200
    assert v1_h.json()["status"] == "ok"

    v1_r = client.get("/api/v1/readiness")
    assert v1_r.status_code == 200
    assert v1_r.json()["status"] == "ready"
