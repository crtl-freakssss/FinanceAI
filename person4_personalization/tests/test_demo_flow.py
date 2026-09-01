from fastapi.testclient import TestClient
from app import app
from examples.person4_client import Person4Client

client = TestClient(app)
sdk = Person4Client(client_session=client)


# ============================================================
# END-TO-END HACKATHON DEMO USER JOURNEY
# ============================================================

def test_complete_demo_journey_moderate_user():
    """
    Simulates the complete end-to-end user journey for the hackathon demo:
    1. Verify service health and database readiness.
    2. Retrieve declared investor profile and constraints.
    3. Retrieve current portfolio asset holdings.
    4. Compute portfolio intelligence (allocation, concentration, health score).
    5. Run advanced quantitative risk engine (volatility, drawdown, sector concentration).
    6. Analyze observed behavioral trading history and investor archetype.
    7. Generate personalized suitability context for stock candidate (RELIANCE.NS).
    """
    # 1. System Readiness
    readiness = sdk.get_readiness()
    assert readiness["status"] == "ready"
    assert readiness["database"] == "connected"

    # 2. Investor Profile
    profile = sdk.get_profile("moderate_001")
    assert profile["user_id"] == "moderate_001"
    assert profile["risk_tolerance"] == "MODERATE"
    assert profile["capital"] == 500000.0

    # 3. Portfolio Holdings
    portfolio = sdk.get_portfolio("moderate_001")
    assert portfolio["user_id"] == "moderate_001"
    assert len(portfolio["holdings"]) == 3
    assert portfolio["cash"] == 150000.0

    # 4. Portfolio Intelligence & Analytics
    analysis = sdk.get_portfolio_analysis("moderate_001")
    assert analysis["user_id"] == "moderate_001"
    assert analysis["total_value"] == 500000.0
    assert analysis["health"]["status"] in ("HEALTHY", "MODERATE", "STRESSED")
    assert 0 <= analysis["concentration"]["concentration_score"] <= 100

    # 5. Advanced Quantitative Risk Engine
    adv_risk = sdk.get_advanced_risk("moderate_001")
    assert adv_risk["user_id"] == "moderate_001"
    assert "volatility" in adv_risk
    assert "drawdown" in adv_risk
    assert adv_risk["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    # 6. Behavioral Profiling & Archetype
    inv_profile = sdk.get_investor_profile("moderate_001")
    assert inv_profile["user_id"] == "moderate_001"
    assert inv_profile["declared_risk_profile"] == "MODERATE"
    assert inv_profile["alignment"] in ("ALIGNED", "PARTIALLY_ALIGNED", "MISALIGNED")

    # 7. Personalized Recommendation Context (Person 1 Hand-off)
    context = sdk.get_personalization_context(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        sector="Energy",
        market_cap="LARGE",
        volatility="HIGH",
    )
    assert context["user_id"] == "moderate_001"
    assert context["symbol"] == "RELIANCE.NS"
    assert context["suitability"] in ("SUITABLE", "CAUTION", "UNSUITABLE")
    assert 0 <= context["risk_score"] <= 100
    assert 0 <= context["suitability_score"] <= 100
    assert isinstance(context["reasons"], list)
    assert isinstance(context["warnings"], list)


def test_demo_profile_risk_differentiation():
    """
    Verifies that the demo dataset provides clear risk differentiation
    between conservative, moderate, and aggressive profiles for the same market input.
    """
    symbol = "TCS.NS"
    sector = "Technology"
    mcap = "LARGE"
    vol = "MEDIUM"

    cons_ctx = sdk.get_personalization_context("conservative_001", symbol, sector, mcap, vol)
    mod_ctx = sdk.get_personalization_context("moderate_001", symbol, sector, mcap, vol)
    agg_ctx = sdk.get_personalization_context("aggressive_001", symbol, sector, mcap, vol)

    # Risk scores should reflect respective risk tolerance profiles
    assert cons_ctx["risk_tolerance"] == "CONSERVATIVE"
    assert mod_ctx["risk_tolerance"] == "MODERATE"
    assert agg_ctx["risk_tolerance"] == "AGGRESSIVE"

    assert cons_ctx["risk_score"] < mod_ctx["risk_score"]
    assert mod_ctx["risk_score"] < agg_ctx["risk_score"]
