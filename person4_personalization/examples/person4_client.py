"""
Person 4 HTTP Client SDK
Provides a clean, typed interface for Person 1, Person 2, and Person 3 to consume Person 4's services
over HTTP without depending on internal Python modules.
"""

from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request
import json


class Person4Client:
    """HTTP Client for interacting with Person 4 (Personalization & Portfolio Intelligence API)."""

    def __init__(self, base_url: str = "http://localhost:8000", client_session=None):
        self.base_url = base_url.rstrip("/")
        self.client_session = client_session  # Optional FastAPI TestClient or httpx.Client

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            query_str = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            url = f"{url}?{query_str}"

        # If using FastAPI TestClient directly
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

        # Standard urllib fallback
        data = json.dumps(json_body).encode("utf-8") if json_body else None
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8")
            raise RuntimeError(f"HTTP Error {exc.code}: {err_body}") from exc

    # ============================================================
    # SYSTEM & HEALTH
    # ============================================================

    def get_health(self) -> Dict[str, Any]:
        """Check if Person 4 service is running."""
        return self._request("GET", "/api/v1/health")

    def get_readiness(self) -> Dict[str, Any]:
        """Check if Person 4 database and components are ready."""
        return self._request("GET", "/api/v1/readiness")

    def get_metrics(self) -> Dict[str, Any]:
        """Retrieve observability and runtime metrics."""
        return self._request("GET", "/api/v1/metrics")

    # ============================================================
    # USER & PORTFOLIO
    # ============================================================

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch investor profile by user ID."""
        return self._request("GET", f"/api/v1/users/{user_id}/profile")

    def get_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Fetch user portfolio and holdings."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio")

    # ============================================================
    # PERSONALIZATION CONTEXT (PRIMARY ENTRY POINT FOR PERSON 1)
    # ============================================================

    def get_personalization_context(
        self,
        user_id: str,
        symbol: str,
        sector: str,
        market_cap: str = "ANY",
        volatility: str = "MEDIUM",
    ) -> Dict[str, Any]:
        """
        Evaluate personalized suitability and context for a stock recommendation.
        Used by Person 1 prior to synthesizing the final recommendation.
        """
        params = {
            "sector": sector,
            "market_cap": market_cap,
            "volatility": volatility,
        }
        return self._request("GET", f"/api/v1/users/{user_id}/context/{symbol}", params=params)

    # ============================================================
    # PORTFOLIO INTELLIGENCE & ANALYTICS (FOR PERSON 3 FRONTEND)
    # ============================================================

    def get_portfolio_analysis(self, user_id: str) -> Dict[str, Any]:
        """Fetch complete portfolio intelligence, allocation, risk, and health breakdown."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/analysis")

    def get_portfolio_allocation(self, user_id: str) -> Dict[str, Any]:
        """Fetch allocation percentages by symbol and sector."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/allocation")

    def get_portfolio_concentration(self, user_id: str) -> Dict[str, Any]:
        """Fetch Herfindahl concentration index and top holding weights."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/concentration")

    def get_portfolio_risk(self, user_id: str) -> Dict[str, Any]:
        """Fetch standard portfolio risk score and risk level."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/risk")

    def get_advanced_risk(self, user_id: str) -> Dict[str, Any]:
        """Fetch advanced quantitative risk analysis (volatility, max drawdown, sector risk)."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/risk/advanced")

    def get_portfolio_health(self, user_id: str) -> Dict[str, Any]:
        """Fetch overall portfolio health score and diversification status."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/health")

    def get_exposure(self, user_id: str, symbol: str, sector: str = "Unknown") -> Dict[str, Any]:
        """Evaluate exposure to a specific stock and its sector within the portfolio."""
        return self._request("GET", f"/api/v1/users/{user_id}/portfolio/exposure/{symbol}", params={"sector": sector})

    # ============================================================
    # BEHAVIOR & INVESTOR PROFILING
    # ============================================================

    def get_behavior(self, user_id: str) -> Dict[str, Any]:
        """Fetch behavioral trading pattern assessment and flags."""
        return self._request("GET", f"/api/v1/users/{user_id}/behavior")

    def get_investor_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch investor profile alignment and behavioral archetype."""
        return self._request("GET", f"/api/v1/users/{user_id}/investor-profile")
