"""
StIC to Unified Backend HTTP API Client
Consumes Person 4, Person 2, and Person 1 Public APIs (/api/v1/...) cleanly without direct internal Python imports.
"""

from typing import Any, Dict, Optional
import urllib.parse
import urllib.request
import json
import os
from stic.config import stic_config


class StICPerson4Client:
    """HTTP Client used by StIC adapters and MCP tools to consume the unified backend."""

    def __init__(self, base_url: Optional[str] = None, client_session: Optional[Any] = None):
        self.base_url = (base_url or os.getenv("STIC_BACKEND_URL", stic_config.PERSON4_API_URL)).rstrip("/")
        self.client_session = client_session  # Optional TestClient for in-process testing

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            query_str = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            url = f"{url}?{query_str}"

        # If using TestClient directly
        if self.client_session is not None:
            func = getattr(self.client_session, method.lower())
            kwargs = {}
            if params is not None:
                kwargs["params"] = params
            if json_body is not None:
                kwargs["json"] = json_body
            resp = func(path, **kwargs)
            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP Error {resp.status_code}: {resp.text}")
            return resp.json()

        # Standard HTTP via urllib with 10s sensible timeout
        data = json.dumps(json_body).encode("utf-8") if json_body else None
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Client-Source": "StIC-SI-Terminal",
        }
        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8")
            raise RuntimeError(f"HTTP Error {exc.code}: {err_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Backend Unavailable Error: {str(exc.reason)}") from exc

    # ============================================================
    # SYSTEM HEALTH & STATUS
    # ============================================================

    def get_health(self) -> Dict[str, Any]:
        """Check service health."""
        return self._request("GET", "/api/v1/health")

    def get_readiness(self) -> Dict[str, Any]:
        """Check database and component readiness."""
        return self._request("GET", "/api/v1/readiness")

    # ============================================================
    # PERSON 4: PROFILES & PORTFOLIO INTELLIGENCE
    # ============================================================

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch investor profile and risk tolerance."""
        return self._request("GET", f"/api/v1/users/{user_id}/profile")

    def get_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Fetch user portfolio and cash balances."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio")

    def get_portfolio_analysis(self, user_id: str) -> Dict[str, Any]:
        """Fetch complete portfolio intelligence, allocation, and health."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/analysis")

    def get_portfolio_allocation(self, user_id: str) -> Dict[str, Any]:
        """Fetch asset and sector allocation weights."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/allocation")

    def get_advanced_risk(self, user_id: str) -> Dict[str, Any]:
        """Fetch advanced quantitative risk analytics (volatility, max drawdown, stress factors)."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/risk/advanced")

    def get_portfolio_health(self, user_id: str) -> Dict[str, Any]:
        """Fetch portfolio health score and warnings."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/health")

    def get_personalization_context(
        self,
        user_id: str,
        symbol: str,
        sector: str = "Unknown",
        market_cap: str = "ANY",
        volatility: str = "MEDIUM",
    ) -> Dict[str, Any]:
        """Fetch personalized suitability scoring for a target stock."""
        params = {
            "sector": sector,
            "market_cap": market_cap,
            "volatility": volatility,
        }
        return self._request("GET", f"/api/v1/users/{user_id}/context/{symbol}", params=params)

    def get_behavior(self, user_id: str) -> Dict[str, Any]:
        """Fetch trading behavior pattern analysis."""
        return self._request("GET", f"/api/v1/users/{user_id}/behavior")

    def get_investor_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch investor archetype and declared vs observed risk alignment."""
        return self._request("GET", f"/api/v1/users/{user_id}/investor-profile")

    # ============================================================
    # PERSON 2: MARKET, INDICATORS, NEWS & RAG
    # ============================================================

    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch live/cached quote data for a symbol."""
        return self._request("GET", f"/api/v1/market/{symbol}")

    def get_market_history(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """Fetch historical price series for a symbol."""
        return self._request("GET", f"/api/v1/market/{symbol}/history", params={"period": period})

    def get_market_indicators(self, symbol: str, period: str = "3mo") -> Dict[str, Any]:
        """Fetch computed technical indicators for a symbol."""
        return self._request("GET", f"/api/v1/market/{symbol}/indicators", params={"period": period})

    def get_news(self, symbol: str) -> Dict[str, Any]:
        """Fetch latest financial news and sentiment for a symbol."""
        return self._request("GET", f"/api/v1/news/{symbol}")

    def query_rag(self, query: str, symbol: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """Query corporate filings and financial documents via RAG."""
        payload = {
            "query": query,
            "symbol": symbol,
            "top_k": top_k,
        }
        return self._request("POST", "/api/v1/rag/query", json_body=payload)

    # ============================================================
    # PERSON 1: MULTI-AGENT AI ANALYSIS
    # ============================================================

    def run_multi_agent_analysis(
        self,
        user_id: str,
        symbol: str,
        analysis_type: str = "full",
        include_rag: bool = True,
        include_news: bool = True,
    ) -> Dict[str, Any]:
        """Trigger automated 5-Agent parallel AI analysis."""
        payload = {
            "user_id": user_id,
            "symbol": symbol,
            "analysis_type": analysis_type,
            "include_rag": include_rag,
            "include_news": include_news,
        }
        return self._request("POST", "/api/v1/ai/analyze", json_body=payload)
