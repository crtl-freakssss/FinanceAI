"""
Test Suite for StIC MCP Server Integration (Step 4).
Validates all 10 MCP tools, tool schemas, in-process execution via TestClient,
and error handling without external network dependencies or secret leakage.
"""

import pytest
from fastapi.testclient import TestClient
from app import app
from stic.client.stic_person4_client import StICPerson4Client
from stic.mcp.server import StICMCPServer


@pytest.fixture
def mcp_server():
    test_http_client = TestClient(app)
    client = StICPerson4Client(base_url="http://testserver", client_session=test_http_client)
    return StICMCPServer(client=client)


# ============================================================
# 1. MCP SERVER INITIALIZATION & TOOL DEFINITIONS
# ============================================================

def test_mcp_server_loads(mcp_server):
    assert mcp_server is not None
    assert mcp_server.client is not None


def test_mcp_tool_definitions_complete(mcp_server):
    tool_defs = mcp_server.get_tool_definitions()
    assert isinstance(tool_defs, list)
    assert len(tool_defs) >= 10

    tool_names = [t["name"] for t in tool_defs]
    expected_tools = [
        "stic_run_multi_agent_analysis",
        "stic_query_financial_rag",
        "stic_get_market_data",
        "stic_get_market_indicators",
        "stic_get_news",
        "stic_get_portfolio_intelligence",
        "stic_get_user_behavior",
        "stic_get_advanced_risk",
        "stic_get_personalization_context",
        "stic_get_terminal_dashboard_data",
        "stic_get_user_profile",
        "stic_get_user_holdings",
    ]
    for expected in expected_tools:
        assert expected in tool_names, f"Tool '{expected}' missing from MCP definitions"


# ============================================================
# 2. PERSON 1 MULTI-AGENT AI TOOL TEST
# ============================================================

def test_mcp_run_multi_agent_analysis(mcp_server):
    result = mcp_server.stic_run_multi_agent_analysis(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        analysis_type="full",
        include_rag=True,
        include_news=True,
    )
    assert isinstance(result, dict)
    assert result["user_id"] == "moderate_001"
    assert result["normalized_symbol"] == "RELIANCE.NS"
    assert result["overall_signal"] in ["BUY", "HOLD", "SELL", "AVOID"]
    assert "confidence" in result
    assert "metrics" in result


# ============================================================
# 3. PERSON 2 TOOLS: RAG, MARKET, INDICATORS, NEWS
# ============================================================

def test_mcp_query_financial_rag(mcp_server):
    result = mcp_server.stic_query_financial_rag(
        query="Reliance revenue growth and operating profit",
        symbol="RELIANCE.NS",
        top_k=3,
    )
    assert isinstance(result, dict)
    assert "results" in result
    assert isinstance(result["results"], list)


def test_mcp_get_market_data(mcp_server):
    result = mcp_server.stic_get_market_data(symbol="TCS.NS")
    assert isinstance(result, dict)
    assert result["symbol"] == "TCS.NS"
    assert "price" in result


def test_mcp_get_market_indicators(mcp_server):
    result = mcp_server.stic_get_market_indicators(symbol="INFY.NS", period="3mo")
    assert isinstance(result, dict)
    assert "rsi" in result
    assert "macd" in result


def test_mcp_get_news(mcp_server):
    result = mcp_server.stic_get_news(symbol="HDFCBANK.NS")
    assert isinstance(result, dict)
    assert "articles" in result
    assert "sentiment" in result


# ============================================================
# 4. PERSON 4 TOOLS: PORTFOLIO, BEHAVIOR, RISK, CONTEXT
# ============================================================

def test_mcp_get_portfolio_intelligence(mcp_server):
    result = mcp_server.stic_get_portfolio_intelligence(user_id="moderate_001")
    assert isinstance(result, dict)
    assert "total_value" in result
    assert "holdings" in result
    assert "health_score" in result


def test_mcp_get_user_behavior(mcp_server):
    result = mcp_server.stic_get_user_behavior(user_id="moderate_001")
    assert isinstance(result, dict)
    assert result["user_id"] == "moderate_001"
    assert "behaviour_score" in result


def test_mcp_get_investor_behavior_profile(mcp_server):
    result = mcp_server.stic_get_investor_behavior_profile(user_id="moderate_001")
    assert isinstance(result, dict)
    assert "investor_type" in result
    assert "observed_risk_profile" in result



def test_mcp_get_advanced_risk(mcp_server):
    result = mcp_server.stic_get_advanced_risk(user_id="moderate_001")
    assert isinstance(result, dict)
    assert result["user_id"] == "moderate_001"
    assert "risk_score" in result

    # Test alias
    alias_result = mcp_server.stic_get_advanced_risk_report(user_id="moderate_001")
    assert alias_result["user_id"] == "moderate_001"


def test_mcp_get_personalization_context(mcp_server):
    result = mcp_server.stic_get_personalization_context(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        sector="Energy",
    )
    assert isinstance(result, dict)
    assert result["user_id"] == "moderate_001"
    assert "suitability" in result


def test_mcp_get_user_profile_and_holdings(mcp_server):
    profile = mcp_server.stic_get_user_profile(user_id="moderate_001")
    assert profile["user_id"] == "moderate_001"

    holdings = mcp_server.stic_get_user_holdings(user_id="moderate_001")
    assert holdings["user_id"] == "moderate_001"


# ============================================================
# 5. DASHBOARD AGGREGATION & ERROR HANDLING TESTS
# ============================================================

def test_mcp_get_terminal_dashboard_data(mcp_server):
    result = mcp_server.stic_get_terminal_dashboard_data(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
    )
    assert isinstance(result, dict)
    assert result["user_id"] == "moderate_001"
    assert "portfolio" in result
    assert "ai_insights" in result
    assert "meta" in result
    assert result["meta"]["target_symbol"] == "RELIANCE.NS"


def test_mcp_invalid_user_handling(mcp_server):
    with pytest.raises(RuntimeError) as exc_info:
        mcp_server.stic_get_user_profile(user_id="unknown_user_404")
    assert "404" in str(exc_info.value)


def test_mcp_invalid_symbol_handling(mcp_server):
    with pytest.raises(RuntimeError) as exc_info:
        mcp_server.stic_get_market_data(symbol="   ")
    assert "422" in str(exc_info.value)


def test_mcp_backend_unavailable_handling():
    # Construct client with unreachable port
    unreachable_client = StICPerson4Client(base_url="http://127.0.0.1:59999")
    unreachable_mcp = StICMCPServer(client=unreachable_client)
    with pytest.raises(RuntimeError) as exc_info:
        unreachable_mcp.stic_get_market_data(symbol="RELIANCE.NS")
    assert "Backend Unavailable" in str(exc_info.value) or "HTTP Error" in str(exc_info.value) or "Error" in str(exc_info.value)


def test_mcp_no_secret_leakage(mcp_server):
    dashboard = mcp_server.stic_get_terminal_dashboard_data(user_id="moderate_001")
    dashboard_str = str(dashboard)

    forbidden_patterns = ["password", "secret_key", "OPENAI_API_KEY", "DATABASE_URL"]
    for pattern in forbidden_patterns:
        assert pattern not in dashboard_str
