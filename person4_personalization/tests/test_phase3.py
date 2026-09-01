from fastapi.testclient import TestClient

from app import app

from portfolio.risk_engine import (
    calculate_advanced_risk,
    calculate_maximum_drawdown,
    calculate_returns,
    calculate_volatility,
    risk_level_from_score,
)

from portfolio.service import get_portfolio
from profile.service import get_profile


client = TestClient(app)


# ============================================================
# RETURNS
# ============================================================

def test_calculate_returns():
    prices = [100, 110, 99]

    result = calculate_returns(prices)

    assert len(result) == 2

    assert round(result[0], 4) == 0.10
    assert round(result[1], 4) == -0.10


# ============================================================
# VOLATILITY
# ============================================================

def test_volatility_with_insufficient_data():
    result = calculate_volatility(
        [100]
    )

    assert result.status == "insufficient_data"
    assert result.value is None


def test_volatility_with_valid_data():
    result = calculate_volatility(
        [
            100,
            102,
            101,
            105,
            103,
            108,
            107,
        ]
    )

    assert result.status == "calculated"

    assert result.value is not None

    assert result.value >= 0

    assert 0 <= result.score <= 100


# ============================================================
# DRAWDOWN
# ============================================================

def test_maximum_drawdown():
    result = calculate_maximum_drawdown(
        [100, 120, 110, 90, 105]
    )

    assert result.status == "calculated"

    assert result.maximum_drawdown is not None

    assert round(
        result.maximum_drawdown,
        2,
    ) == 25.0


def test_drawdown_monotonic_growth():
    result = calculate_maximum_drawdown(
        [100, 110, 120, 130]
    )

    assert result.status == "calculated"

    assert result.maximum_drawdown == 0


def test_drawdown_insufficient_data():
    result = calculate_maximum_drawdown(
        [100]
    )

    assert result.status == "insufficient_data"

    assert result.maximum_drawdown is None


# ============================================================
# RISK LEVEL
# ============================================================

def test_risk_level_low():
    assert risk_level_from_score(0) == "LOW"
    assert risk_level_from_score(29.99) == "LOW"


def test_risk_level_medium():
    assert risk_level_from_score(30) == "MEDIUM"
    assert risk_level_from_score(59.99) == "MEDIUM"


def test_risk_level_high():
    assert risk_level_from_score(60) == "HIGH"
    assert risk_level_from_score(79.99) == "HIGH"


def test_risk_level_critical():
    assert risk_level_from_score(80) == "CRITICAL"
    assert risk_level_from_score(100) == "CRITICAL"


# ============================================================
# COMPLETE ENGINE
# ============================================================

def test_advanced_risk_engine():
    portfolio = get_portfolio(
        "moderate_001"
    )

    user = get_profile(
        "moderate_001"
    )

    assert portfolio is not None
    assert user is not None

    result = calculate_advanced_risk(
        portfolio=portfolio,
        user_profile=user,
    )

    assert result.user_id == "moderate_001"

    assert 0 <= result.risk_score <= 100

    assert result.risk_level in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    assert result.volatility is not None
    assert result.drawdown is not None
    assert result.liquidity is not None

    assert 0 <= result.concentration_score <= 100

    assert 0 <= result.diversification_score <= 100

    assert result.data_quality is not None

    assert isinstance(
        result.risk_factors,
        list,
    )

    assert isinstance(
        result.warnings,
        list,
    )


# ============================================================
# UNKNOWN USER
# ============================================================

def test_advanced_risk_unknown_user():
    response = client.get(
        "/api/users/does_not_exist/"
        "portfolio/risk/advanced"
    )

    assert response.status_code == 404


# ============================================================
# API
# ============================================================

def test_advanced_risk_api():
    response = client.get(
        "/api/users/moderate_001/"
        "portfolio/risk/advanced"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == "moderate_001"

    assert 0 <= body["risk_score"] <= 100

    assert body["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    assert "volatility" in body
    assert "drawdown" in body
    assert "liquidity" in body

    assert "concentration_score" in body
    assert "diversification_score" in body

    assert "risk_factors" in body
    assert "warnings" in body
    assert "data_quality" in body