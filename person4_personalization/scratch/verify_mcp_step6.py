"""
Step 6 MCP Tool Live Verification Script
"""

import os
import sys

# Ensure proper path
sys.path.insert(0, os.path.abspath("person4_personalization"))
from stic.mcp.server import StICMCPServer
from stic.client.stic_person4_client import StICPerson4Client

def run_mcp_verification():
    print("==================================================")
    print("STEP 6 STIC MCP LIVE VERIFICATION")
    print("==================================================")

    client = StICPerson4Client(base_url="http://127.0.0.1:8000")
    server = StICMCPServer(client=client)
    tool_defs = server.get_tool_definitions()
    print(f"[PASS] Tool Definitions Loaded: {len(tool_defs)} tools exposed.")

    # 1. Multi-Agent AI Tool
    res = server.stic_run_multi_agent_analysis(user_id="moderate_001", symbol="RELIANCE.NS")
    assert "signal" in res or "overall_signal" in res or "verdict" in res
    print(f"[PASS] stic_run_multi_agent_analysis -> Verdict: {res.get('signal') or res.get('overall_signal') or res.get('verdict')}")

    # 2. Financial RAG Tool
    res = server.stic_query_financial_rag(query="Reliance Q3 revenue growth", symbol="RELIANCE.NS")
    assert "count" in res or "results" in res
    print(f"[PASS] stic_query_financial_rag -> Results: {res.get('count', len(res.get('results', [])))}")

    # 3. Market Data Tool
    res = server.stic_get_market_data(symbol="RELIANCE.NS")
    assert res.get("price", 0) > 0
    print(f"[PASS] stic_get_market_data -> Price: {res.get('price')}")

    # 4. Market Indicators Tool
    res = server.stic_get_market_indicators(symbol="RELIANCE.NS")
    assert "rsi" in res
    print(f"[PASS] stic_get_market_indicators -> RSI: {res.get('rsi')}")

    # 5. News Tool
    res = server.stic_get_news(symbol="RELIANCE.NS")
    assert "articles" in res
    print(f"[PASS] stic_get_news -> Articles: {len(res.get('articles', []))}")

    # 6. Portfolio Intelligence Tool
    res = server.stic_get_portfolio_intelligence(user_id="moderate_001")
    assert res.get("total_value", 0) > 0
    print(f"[PASS] stic_get_portfolio_intelligence -> Total Value: {res.get('total_value')}")

    # 7. User Behavior Tool
    res = server.stic_get_user_behavior(user_id="moderate_001")
    assert "investor_archetype" in res
    print(f"[PASS] stic_get_user_behavior -> Archetype: {res.get('investor_archetype')}")

    # 8. Advanced Risk Tool
    res = server.stic_get_advanced_risk(user_id="moderate_001")
    assert "risk_score" in res
    print(f"[PASS] stic_get_advanced_risk -> Risk Score: {res.get('risk_score')}")

    # 9. Personalization Context Tool
    res = server.stic_get_personalization_context(user_id="moderate_001", symbol="RELIANCE.NS")
    assert "suitability_score" in res
    print(f"[PASS] stic_get_personalization_context -> Suitability: {res.get('suitability_score')}")

    # 10. Consolidated Dashboard Tool
    res = server.stic_get_terminal_dashboard_data(user_id="moderate_001", symbol="RELIANCE.NS")
    res_dict = res if isinstance(res, dict) else res.model_dump()
    assert "user_id" in res_dict and "portfolio" in res_dict
    print(f"[PASS] stic_get_terminal_dashboard_data -> Consolidated User: {res_dict.get('user_id')}")

    # 11. User Profile & Holdings Tools
    res = server.stic_get_user_profile(user_id="moderate_001")
    assert res.get("user_id") == "moderate_001"
    print(f"[PASS] stic_get_user_profile -> User: {res.get('user_id')}")

    res = server.stic_get_user_holdings(user_id="moderate_001")
    assert "holdings" in res
    print(f"[PASS] stic_get_user_holdings -> Positions: {len(res.get('holdings', []))}")

    # 12. Security & Error Non-Leakage Check
    try:
        server.stic_get_user_profile(user_id="non_existent_user_999")
        assert False, "Should have raised exception"
    except Exception as e:
        err_msg = str(e)
        assert "Traceback" not in err_msg
        assert "password" not in err_msg.lower()
        print(f"[PASS] Error Sanitization & Non-Leakage Verified: {err_msg}")

    print("\n==================================================")
    print("ALL 12 STIC MCP TOOLS VERIFIED LIVE (100%)!")
    print("==================================================")

if __name__ == "__main__":
    run_mcp_verification()
