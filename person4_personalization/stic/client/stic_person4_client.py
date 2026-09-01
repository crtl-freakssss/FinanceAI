"""
StIC to Person 4 HTTP API Client
Consumes Person 4 Public API (/api/v1/...) cleanly without direct internal Python imports.
"""

from typing import Any, Dict, Optional
import urllib.parse
import urllib.request
import json
from stic.config import stic_config


class StICPerson4Client:
    """HTTP Client used by StIC adapters and MCP tools to consume Person 4."""

    def __init__(self, base_url: Optional[str] = None, client_session: Optional[Any] = None):
        self.base_url = (base_url or stic_config.PERSON4_API_URL).rstrip("/")
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

        # Standard HTTP via urllib
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

    # ============================================================
    # PUBLIC PERSON 4 CONTRACT METHODS
    # ============================================================

    def get_health(self) -> Dict[str, Any]:
        """Check Person 4 service health."""
        return self._request("GET", "/api/v1/health")

    def get_readiness(self) -> Dict[str, Any]:
        """Check Person 4 database and components readiness."""
        return self._request("GET", "/api/v1/readiness")

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
