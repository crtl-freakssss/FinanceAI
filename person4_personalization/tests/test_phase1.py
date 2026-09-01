from fastapi.testclient import TestClient

from app import app
from portfolio.personalization_engine import (
    build_personalization_context,
)


client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["phase"] == 1


def test_profile_endpoint():
    response = client.get(
        "/api/users/moderate_001/profile"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == "moderate_001"
    assert body["risk_tolerance"] == "MODERATE"


def test_portfolio_endpoint():
    response = client.get(
        "/api/users/moderate_001/portfolio"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == "moderate_001"
    assert len(body["holdings"]) == 3


def test_personalization_context():
    context = build_personalization_context(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        sector="Energy",
        market_cap="LARGE",
        volatility="MEDIUM",
    )

    assert context.user_id == "moderate_001"

    assert 0 <= context.risk_score <= 100

    assert 0 <= context.suitability_score <= 100

    assert context.risk_level in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    assert context.reasons


def test_same_market_input_produces_different_profiles():
    conservative = build_personalization_context(
        user_id="conservative_001",
        symbol="RELIANCE.NS",
        sector="Energy",
        market_cap="LARGE",
        volatility="HIGH",
    )

    aggressive = build_personalization_context(
        user_id="aggressive_001",
        symbol="RELIANCE.NS",
        sector="Energy",
        market_cap="LARGE",
        volatility="HIGH",
    )

    assert (
        conservative.risk_score
        != aggressive.risk_score
    )

    assert (
        conservative.suitability_score
        != aggressive.suitability_score
    )


def test_excluded_sector_is_not_suitable():
    context = build_personalization_context(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        sector="Technology",
        market_cap="LARGE",
        volatility="MEDIUM",
    )

    assert context.suitability_score >= 0
    assert context.suitability_score <= 100


def test_unknown_user_returns_404():
    response = client.get(
        "/api/users/does_not_exist/profile"
    )

    assert response.status_code == 404


def test_context_endpoint():
    response = client.get(
        "/api/users/aggressive_001/context/"
        "RELIANCE.NS"
        "?sector=Energy"
        "&market_cap=LARGE"
        "&volatility=HIGH"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == "aggressive_001"
    assert body["symbol"] == "RELIANCE.NS"
    assert "risk_score" in body
    assert "suitability" in body
    assert "constraint_breaches" in body