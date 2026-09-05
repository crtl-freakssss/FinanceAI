from fastapi.testclient import TestClient

from app import app
from portfolio.analytics import (
    calculate_allocation,
    calculate_concentration,
    calculate_diversification_score,
    calculate_exposure,
    calculate_portfolio_analysis,
    calculate_portfolio_health,
    calculate_portfolio_risk,
)
from portfolio.service import get_portfolio
from profile.service import get_user_profile


client = TestClient(app)


def test_allocation_percentages_are_valid():
    portfolio = get_portfolio("moderate_001")

    result = calculate_allocation(portfolio)

    assert result.by_symbol
    assert result.by_sector

    for item in result.by_symbol:
        assert 0 <= item.percentage <= 100

    for item in result.by_sector:
        assert 0 <= item.percentage <= 100


def test_concentration_score_is_bounded():
    portfolio = get_portfolio("moderate_001")

    result = calculate_concentration(portfolio)

    assert 0 <= result.concentration_score <= 100
    assert 0 <= result.largest_position_percent <= 100
    assert 0 <= result.top_three_position_percent <= 100
    assert 0 <= result.largest_sector_percent <= 100

    assert result.concentration_level in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }


def test_diversification_score_is_bounded():
    portfolio = get_portfolio("moderate_001")

    concentration = calculate_concentration(
        portfolio,
    )

    score = calculate_diversification_score(
        portfolio,
        concentration,
    )

    assert 0 <= score <= 100


def test_exposure_calculation():
    user = get_user_profile("moderate_001")
    portfolio = get_portfolio("moderate_001")

    result = calculate_exposure(
        portfolio,
        user,
        "RELIANCE.NS",
        "Energy",
    )

    assert result.symbol == "RELIANCE.NS"
    assert result.sector == "Energy"

    assert result.position_value >= 0
    assert 0 <= result.position_exposure_percent <= 100

    assert result.sector_value >= 0
    assert 0 <= result.sector_exposure_percent <= 100


def test_position_breach_is_detected():
    user = get_user_profile("conservative_001")
    portfolio = get_portfolio("conservative_001")

    result = calculate_exposure(
        portfolio,
        user,
        "RELIANCE.NS",
        "Energy",
    )

    assert result.position_exposure_percent > 0

    if (
        result.position_exposure_percent
        > result.max_position_percent
    ):
        assert result.position_breach is True


def test_sector_breach_is_detected():
    user = get_user_profile("moderate_001")
    portfolio = get_portfolio("moderate_001")

    result = calculate_exposure(
        portfolio,
        user,
        "TCS.NS",
        "Technology",
    )

    assert result.sector_exposure_percent > 0

    if (
        result.sector_exposure_percent
        > result.max_sector_percent
    ):
        assert result.sector_breach is True


def test_portfolio_risk():
    portfolio = get_portfolio("moderate_001")

    concentration = calculate_concentration(
        portfolio,
    )

    result = calculate_portfolio_risk(
        portfolio,
        concentration,
    )

    assert 0 <= result.risk_score <= 100
    assert 0 <= result.concentration_score <= 100
    assert 0 <= result.diversification_score <= 100
    assert 0 <= result.cash_percent <= 100

    assert result.risk_level in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }


def test_portfolio_health():
    portfolio = get_portfolio("moderate_001")

    concentration = calculate_concentration(
        portfolio,
    )

    risk = calculate_portfolio_risk(
        portfolio,
        concentration,
    )

    result = calculate_portfolio_health(
        portfolio,
        concentration,
        risk,
    )

    assert 0 <= result.health_score <= 100
    assert 0 <= result.diversification_score <= 100
    assert 0 <= result.concentration_score <= 100

    assert result.status in {
        "HEALTHY",
        "MODERATE",
        "STRESSED",
    }


def test_complete_portfolio_analysis():
    portfolio = get_portfolio("moderate_001")

    result = calculate_portfolio_analysis(
        portfolio,
    )

    assert result.user_id == "moderate_001"

    assert result.total_value > 0

    assert (
        result.total_value
        == result.holdings_value + result.cash_value
    )

    assert 0 <= result.cash_percent <= 100
    assert 0 <= result.equity_percent <= 100

    assert result.allocation
    assert result.concentration
    assert result.risk
    assert result.health


def test_api_portfolio_analysis():
    response = client.get(
        "/api/users/moderate_001/portfolio/analysis"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == "moderate_001"
    assert body["total_value"] > 0

    assert "allocation" in body
    assert "concentration" in body
    assert "risk" in body
    assert "health" in body


def test_api_allocation():
    response = client.get(
        "/api/users/moderate_001/portfolio/allocation"
    )

    assert response.status_code == 200

    body = response.json()

    assert "by_symbol" in body
    assert "by_sector" in body


def test_api_concentration():
    response = client.get(
        "/api/users/moderate_001/portfolio/concentration"
    )

    assert response.status_code == 200

    body = response.json()

    assert "concentration_score" in body
    assert "largest_position_percent" in body


def test_api_risk():
    response = client.get(
        "/api/users/moderate_001/portfolio/risk"
    )

    assert response.status_code == 200

    body = response.json()

    assert "risk_score" in body
    assert "risk_level" in body
    assert "diversification_score" in body


def test_api_health():
    response = client.get(
        "/api/users/moderate_001/portfolio/health"
    )

    assert response.status_code == 200

    body = response.json()

    assert "health_score" in body
    assert "status" in body


def test_api_exposure():
    response = client.get(
        "/api/users/moderate_001/portfolio/exposure/"
        "RELIANCE.NS?sector=Energy"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["symbol"] == "RELIANCE.NS"
    assert body["sector"] == "Energy"
    assert "position_breach" in body
    assert "sector_breach" in body


def test_unknown_portfolio_user_returns_404():
    response = client.get(
        "/api/users/does_not_exist/"
        "portfolio/analysis"
    )

    assert response.status_code == 404