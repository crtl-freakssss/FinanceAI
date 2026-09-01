from fastapi.testclient import TestClient

from app import app

from behavior.analyzer import analyze_behavior
from behavior.transaction_analyzer import (
    calculate_holding_periods,
    calculate_trading_statistics,
)

from profile.investor_profiler import (
    build_investor_profile,
)

from profile.service import get_profile


client = TestClient(app)


# ============================================================
# TRANSACTION ANALYSIS
# ============================================================

def test_trading_statistics():
    transactions = [
        {
            "transaction_type": "BUY",
            "quantity": 10,
            "price": 100,
        },
        {
            "transaction_type": "SELL",
            "quantity": 5,
            "price": 120,
        },
    ]

    result = calculate_trading_statistics(
        transactions
    )

    assert result["total_transactions"] == 2
    assert result["buy_transactions"] == 1
    assert result["sell_transactions"] == 1

    assert result["total_buy_value"] == 1000
    assert result["total_sell_value"] == 600


def test_holding_period_calculation():
    transactions = [
        {
            "symbol": "TEST",
            "transaction_type": "BUY",
            "quantity": 10,
            "price": 100,
            "date": "2026-01-01",
        },
        {
            "symbol": "TEST",
            "transaction_type": "SELL",
            "quantity": 10,
            "price": 120,
            "date": "2026-01-31",
        },
    ]

    periods = calculate_holding_periods(
        transactions
    )

    assert periods == [30]


# ============================================================
# BEHAVIOUR
# ============================================================

def test_conservative_behavior():
    result = analyze_behavior(
        "conservative_001"
    )

    assert (
        result.user_id
        == "conservative_001"
    )

    assert 0 <= result.behaviour_score <= 100

    assert result.trading.total_transactions == 4

    assert result.investor_archetype in {
        "PASSIVE_INVESTOR",
        "LONG_TERM_INVESTOR",
        "BALANCED_INVESTOR",
        "ACTIVE_GROWTH",
        "ACTIVE_TRADER",
    }


def test_moderate_behavior():
    result = analyze_behavior(
        "moderate_001"
    )

    assert (
        result.user_id
        == "moderate_001"
    )

    assert (
        result.trading.total_transactions
        == 6
    )

    assert 0 <= result.behaviour_score <= 100

    assert result.behaviour_risk_level in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }


def test_aggressive_behavior():
    result = analyze_behavior(
        "aggressive_001"
    )

    assert (
        result.user_id
        == "aggressive_001"
    )

    assert (
        result.trading.total_transactions
        == 10
    )

    assert (
        result.trading.trading_frequency
        == "MEDIUM"
    )

    assert 0 <= result.behaviour_score <= 100


# ============================================================
# DATA QUALITY
# ============================================================

def test_unknown_user_has_insufficient_data():
    result = analyze_behavior(
        "does_not_exist"
    )

    assert (
        result.data_quality.overall
        == "insufficient_data"
    )

    assert (
        result.behaviour_score
        == 0
    )


# ============================================================
# INVESTOR PROFILE
# ============================================================

def test_investor_profile():
    profile = get_profile(
        "moderate_001"
    )

    assert profile is not None

    result = build_investor_profile(
        "moderate_001",
        profile,
    )

    assert (
        result.user_id
        == "moderate_001"
    )

    assert result.declared_risk_profile in {
        "CONSERVATIVE",
        "MODERATE",
        "AGGRESSIVE",
    }

    assert result.observed_risk_profile in {
        "CONSERVATIVE",
        "MODERATE",
        "AGGRESSIVE",
    }

    assert result.alignment in {
        "ALIGNED",
        "PARTIALLY_ALIGNED",
        "MISALIGNED",
    }

    assert 0 <= result.profile_confidence <= 100


# ============================================================
# API
# ============================================================

def test_behavior_api():
    response = client.get(
        "/api/users/moderate_001/behavior"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == "moderate_001"

    assert "behaviour_score" in body
    assert "trading" in body
    assert "holding_period" in body
    assert "performance" in body
    assert "behaviour_flags" in body
    assert "data_quality" in body


def test_investor_profile_api():
    response = client.get(
        "/api/users/moderate_001/"
        "investor-profile"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == "moderate_001"

    assert "declared_risk_profile" in body
    assert "observed_risk_profile" in body
    assert "investor_type" in body
    assert "alignment" in body
    assert "profile_confidence" in body


def test_behavior_unknown_user():
    response = client.get(
        "/api/users/does_not_exist/behavior"
    )

    assert response.status_code == 404


def test_investor_profile_unknown_user():
    response = client.get(
        "/api/users/does_not_exist/"
        "investor-profile"
    )

    assert response.status_code == 404