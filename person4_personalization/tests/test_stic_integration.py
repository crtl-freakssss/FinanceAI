"""
StIC MCP & SI Terminal Integration Test Suite
Validates that StIC client, adapters, schemas, and MCP tools cleanly interface with Person 4.
"""

import pytest
from fastapi.testclient import TestClient
from app import app
from stic.client.stic_person4_client import StICPerson4Client
from stic.adapters.portfolio_adapter import StICPortfolioAdapter
from stic.adapters.ai_insights_adapter import StICAIInsightsAdapter
from stic.mcp.server import StICMCPServer
from stic.schemas.stic_models import (
    SITerminalPortfolioView,
    SITerminalAIInsightsView,
    SITerminalFullDashboard,
)
from stic.config import stic_config


@pytest.fixture
def client_session():
    """FastAPI TestClient fixture for in-process HTTP testing."""
    return TestClient(app)


@pytest.fixture
def stic_client(client_session):
    """StIC Person 4 Client wired to in-process test client."""
    return StICPerson4Client(base_url="http://testserver", client_session=client_session)


@pytest.fixture
def mcp_server(stic_client):
    """StIC MCP Server fixture."""
    return StICMCPServer(client=stic_client)


# ============================================================
# 1. CLIENT TESTS
# ============================================================

def test_stic_client_health_and_readiness(stic_client):
    health = stic_client.get_health()
    assert health["status"] == "ok"
    assert health["service"] == "finance-personalization"

    readiness = stic_client.get_readiness()
    assert readiness["status"] == "ready"
    assert readiness["database"] == "connected"


def test_stic_client_fetches_profile_and_portfolio(stic_client):
    profile = stic_client.get_profile("moderate_001")
    assert profile["user_id"] == "moderate_001"
    assert profile["risk_tolerance"] == "MODERATE"

    portfolio = stic_client.get_portfolio("moderate_001")
    assert portfolio["user_id"] == "moderate_001"
    assert len(portfolio["holdings"]) > 0


def test_stic_client_personalization_context(stic_client):
    context = stic_client.get_personalization_context(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        sector="Energy",
        market_cap="LARGE",
        volatility="HIGH",
    )
    assert context["user_id"] == "moderate_001"
    assert context["symbol"] == "RELIANCE.NS"
    assert "suitability_score" in context
    assert "suitability" in context


# ============================================================
# 2. ADAPTER TESTS
# ============================================================

def test_portfolio_adapter_transforms_data(stic_client):
    adapter = StICPortfolioAdapter(stic_client)
    view = adapter.get_terminal_portfolio_view("moderate_001")

    assert isinstance(view, SITerminalPortfolioView)
    assert view.user_id == "moderate_001"
    assert view.total_value > 0
    assert view.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert len(view.holdings) >= 3
    assert len(view.sector_breakdown) >= 1

    # Verify holding math and fields
    first_h = view.holdings[0]
    assert first_h.symbol != ""
    assert first_h.shares > 0
    assert first_h.weight_percent > 0


def test_ai_insights_adapter_transforms_data(stic_client):
    adapter = StICAIInsightsAdapter(stic_client)
    view = adapter.get_terminal_ai_insights_view("moderate_001")

    assert isinstance(view, SITerminalAIInsightsView)
    assert view.user_id == "moderate_001"
    assert view.declared_risk_profile == "MODERATE"
    assert view.sentiment_score >= 0 and view.sentiment_score <= 100
    assert view.consensus_action in ["BUY", "HOLD", "REBALANCE", "CAUTION"]
    assert len(view.signals) >= 2


# ============================================================
# 3. MCP SERVER & TOOL EXECUTION TESTS
# ============================================================

def test_mcp_portfolio_intelligence_tool(mcp_server):
    result = mcp_server.stic_get_portfolio_intelligence(user_id="moderate_001")
    assert result["user_id"] == "moderate_001"
    assert "total_value" in result
    assert "holdings" in result
    assert "health_score" in result


def test_mcp_personalization_context_tool(mcp_server):
    result = mcp_server.stic_get_personalization_context(
        user_id="conservative_001",
        symbol="HDFCBANK.NS",
        sector="Financial Services",
        market_cap="LARGE",
    )
    assert result["user_id"] == "conservative_001"
    assert result["symbol"] == "HDFCBANK.NS"
    assert "suitability_score" in result


def test_mcp_advanced_risk_report_tool(mcp_server):
    result = mcp_server.stic_get_advanced_risk_report(user_id="aggressive_001")
    assert result["user_id"] == "aggressive_001"
    assert "risk_score" in result
    assert "volatility" in result
    assert "drawdown" in result


def test_mcp_investor_behavior_profile_tool(mcp_server):
    result = mcp_server.stic_get_investor_behavior_profile(user_id="aggressive_001")
    assert result["user_id"] == "aggressive_001"
    assert result["observed_risk_profile"] == "AGGRESSIVE"
    assert "signals" in result


def test_mcp_full_terminal_dashboard_data(mcp_server):
    result = mcp_server.stic_get_terminal_dashboard_data(user_id="moderate_001")
    assert result["project_id"] == stic_config.STIC_PROJECT_ID
    assert result["user_id"] == "moderate_001"
    assert "portfolio" in result
    assert "ai_insights" in result
    assert result["portfolio"]["total_value"] > 0


def test_mcp_tool_definitions_valid(mcp_server):
    defs = mcp_server.get_tool_definitions()
    assert len(defs) == 5
    tool_names = [t["name"] for t in defs]
    assert "stic_get_portfolio_intelligence" in tool_names
    assert "stic_get_personalization_context" in tool_names
    assert "stic_get_advanced_risk_report" in tool_names
    assert "stic_get_investor_behavior_profile" in tool_names
    assert "stic_get_terminal_dashboard_data" in tool_names
