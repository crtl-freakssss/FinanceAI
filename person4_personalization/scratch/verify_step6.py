"""
Step 6 Complete System Verification Script
Executes all E2E verification checks against the live running FastAPI backend on http://127.0.0.1:8000
"""

import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def get_text(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8")

def post(path, body):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def run_tests():
    print("==================================================")
    print("STEP 6 COMPLETE END-TO-END VERIFICATION")
    print("==================================================")

    # 1. System Health & Docs
    print("\n--- 1. Health, Readiness & Docs ---")
    st, data = get("/health")
    assert st == 200 and data["status"] == "ok"
    print(f"[PASS] GET /health -> {data}")

    st, data = get("/ready")
    assert st == 200 and data["status"] == "ready"
    print(f"[PASS] GET /ready -> {data}")

    st, html = get_text("/docs")
    assert st == 200 and "swagger" in html.lower()
    print(f"[PASS] GET /docs -> Status {st} ({len(html)} bytes)")

    st, html = get_text("/dashboard")
    assert st == 200 and "SI Terminal" in html
    print(f"[PASS] GET /dashboard -> Status {st} ({len(html)} bytes)")

    st, html = get_text("/terminal")
    assert st == 200 and "SI Terminal" in html
    print(f"[PASS] GET /terminal -> Status {st} ({len(html)} bytes)")

    # 2. Person 4 Endpoints
    print("\n--- 2. Person 4 API Chain ---")
    st, profile = get("/api/v1/users/moderate_001/profile")
    assert st == 200 and profile["user_id"] == "moderate_001"
    print(f"[PASS] GET /users/moderate_001/profile -> Risk: {profile.get('risk_tolerance')}")

    st, portfolio = get("/api/v1/users/moderate_001/portfolio")
    assert st == 200 and len(portfolio.get("holdings", [])) > 0
    print(f"[PASS] GET /users/moderate_001/portfolio -> Holdings: {len(portfolio['holdings'])} positions")

    st, analysis = get("/api/v1/users/moderate_001/portfolio/analysis")
    assert st == 200 and analysis["total_value"] > 0
    print(f"[PASS] GET /users/moderate_001/portfolio/analysis -> Total Value: {analysis['total_value']}")

    st, risk = get("/api/v1/users/moderate_001/portfolio/risk/advanced")
    assert st == 200 and "risk_score" in risk
    print(f"[PASS] GET /users/moderate_001/portfolio/risk/advanced -> Risk Score: {risk['risk_score']}")

    st, behavior = get("/api/v1/users/moderate_001/behavior")
    assert st == 200 and "investor_archetype" in behavior
    print(f"[PASS] GET /users/moderate_001/behavior -> Archetype: {behavior.get('investor_archetype')}")

    st, ctx = get("/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy&market_cap=LARGE")
    assert st == 200 and "suitability_score" in ctx
    print(f"[PASS] GET /users/moderate_001/context/RELIANCE.NS -> Suitability: {ctx['suitability']} ({ctx['suitability_score']}/100)")

    # 3. Person 2 Endpoints
    print("\n--- 3. Person 2 API Chain ---")
    st, mkt = get("/api/v1/market/RELIANCE.NS")
    assert st == 200 and mkt["price"] > 0
    print(f"[PASS] GET /market/RELIANCE.NS -> Price: {mkt['price']} ({mkt.get('source', 'live')})")

    st, hist = get("/api/v1/market/RELIANCE.NS/history?period=1mo")
    assert st == 200 and len(hist.get("history", [])) > 0
    print(f"[PASS] GET /market/RELIANCE.NS/history -> {len(hist['history'])} price bars")

    st, ind = get("/api/v1/market/RELIANCE.NS/indicators")
    assert st == 200 and "rsi" in ind
    print(f"[PASS] GET /market/RELIANCE.NS/indicators -> RSI: {ind['rsi']}, MACD: {ind['macd']}, EMA20: {ind.get('ema20')}")

    st, news = get("/api/v1/news/RELIANCE.NS")
    assert st == 200 and "articles" in news
    print(f"[PASS] GET /news/RELIANCE.NS -> {len(news['articles'])} articles")

    st, rag = post("/api/v1/rag/query", {"query": "Reliance Q3 earnings and operating profit", "symbol": "RELIANCE.NS", "top_k": 3})
    assert st == 200
    print(f"[PASS] POST /rag/query -> Results Count: {rag.get('results_count', 0)}")

    # 4. Person 1 Multi-Agent AI Analysis
    print("\n--- 4. Person 1 Multi-Agent AI Analysis ---")
    ai_payload = {
        "user_id": "moderate_001",
        "symbol": "RELIANCE.NS",
        "analysis_type": "full",
        "include_rag": True,
        "include_news": True
    }
    st, ai_resp = post("/api/v1/ai/analyze", ai_payload)
    assert st == 200
    sig = ai_resp.get("overall_signal") or ai_resp.get("verdict")
    conf = ai_resp.get("confidence")
    lat = ai_resp.get("metrics", {}).get("total_latency_ms", ai_resp.get("latency_ms"))
    print(f"[PASS] POST /ai/analyze -> Verdict: {sig} (Confidence: {conf*100:.0f}%, Latency: {lat}ms)")
    agents = ai_resp.get("agents", {})
    for agent_name, agent_data in agents.items():
        print(f"   * {agent_name.capitalize()} Agent: {agent_data.get('signal')} (Confidence: {agent_data.get('confidence')*100:.0f}%)")

    # 5. User Switching Across All Archetypes
    print("\n--- 5. User Switching Verification ---")
    for u in ["moderate_001", "conservative_001", "aggressive_001"]:
        st, p = get(f"/api/v1/users/{u}/portfolio/analysis")
        st, prof = get(f"/api/v1/users/{u}/profile")
        print(f"[PASS] User {u}: Total Value: {p['total_value']}, Risk: {prof.get('risk_tolerance')}")

    # 6. Symbol Switching & Normalization
    print("\n--- 6. Symbol Switching & Normalization ---")
    for sym in ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ITC", "AAPL", "NVDA"]:
        st, q = get(f"/api/v1/market/{sym}")
        print(f"[PASS] Symbol '{sym}' -> Normalized: '{q['symbol']}', Price: {q['price']}")

    # 7. Error & Degradation Handling
    print("\n--- 7. Error & Degradation Isolation ---")
    # 404 for missing user
    try:
        get("/api/v1/users/non_existent_user_999/profile")
        assert False, "Should have 404ed"
    except urllib.error.HTTPError as e:
        assert e.code == 404
        err_msg = json.loads(e.read().decode())
        print(f"[PASS] 404 Unknown User Handled: {err_msg}")

    # 422 for malformed AI request
    try:
        post("/api/v1/ai/analyze", {"user_id": "moderate_001", "symbol": ""})
        assert False, "Should have 422ed"
    except urllib.error.HTTPError as e:
        assert e.code == 422
        print(f"[PASS] 422 Empty Symbol Handled: HTTP {e.code}")

    print("\n==================================================")
    print("ALL STEP 6 END-TO-END VERIFICATIONS PASSED (100%)!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
