"""
StIC MCP Server
Exposes high-level intelligence and portfolio tools powered by Person 4 for AI agents.
"""

from typing import Any, Dict, Optional
from stic.client.stic_person4_client import StICPerson4Client
from stic.adapters.portfolio_adapter import StICPortfolioAdapter
from stic.adapters.ai_insights_adapter import StICAIInsightsAdapter
from stic.schemas.stic_models import (
    SITerminalPortfolioView,
    SITerminalAIInsightsView,
    SITerminalFullDashboard,
)
from stic.config import stic_config


class StICMCPServer:
    """
    Tool handler and execution engine for StIC Model Context Protocol (MCP) tools.
    Connects agents cleanly to Person 4 services without polluting core business logic.
    """

    def __init__(self, client: Optional[StICPerson4Client] = None):
        self.client = client or StICPerson4Client()
        self.portfolio_adapter = StICPortfolioAdapter(self.client)
        self.ai_insights_adapter = StICAIInsightsAdapter(self.client)

    # ============================================================
    # MCP TOOL 1: Portfolio Intelligence
    # ============================================================
    def stic_get_portfolio_intelligence(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve formatted portfolio intelligence, holdings, sector allocation,
        and health metrics for a given user.
        """
        portfolio_view = self.portfolio_adapter.get_terminal_portfolio_view(user_id)
        return portfolio_view.model_dump()

    # ============================================================
    # MCP TOOL 2: Personalization Context
    # ============================================================
    def stic_get_personalization_context(
        self,
        user_id: str,
        symbol: str,
        sector: str = "Unknown",
        market_cap: str = "ANY",
        volatility: str = "MEDIUM",
    ) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve personalization suitability score, warnings, and constraint
        checks for a target stock symbol prior to generating final recommendations.
        """
        return self.client.get_personalization_context(
            user_id=user_id,
            symbol=symbol,
            sector=sector,
            market_cap=market_cap,
            volatility=volatility,
        )

    # ============================================================
    # MCP TOOL 3: Advanced Risk Analytics
    # ============================================================
    def stic_get_advanced_risk_report(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve quantitative risk metrics including annualized volatility,
        historical maximum drawdown, and portfolio risk factor breakdowns.
        """
        return self.client.get_advanced_risk(user_id)

    # ============================================================
    # MCP TOOL 4: Investor Behavioral Profile
    # ============================================================
    def stic_get_investor_behavior_profile(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve investor trading archetype, declared vs observed risk alignment,
        and synthesized AI insight signals.
        """
        ai_view = self.ai_insights_adapter.get_terminal_ai_insights_view(user_id)
        return ai_view.model_dump()

    # ============================================================
    # MCP TOOL 5: Full SI Terminal Aggregated Payload
    # ============================================================
    def stic_get_terminal_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve complete unified payload powering the SI Terminal Intelligence Platform.
        """
        profile = self.client.get_profile(user_id)
        portfolio_view = self.portfolio_adapter.get_terminal_portfolio_view(user_id)
        ai_view = self.ai_insights_adapter.get_terminal_ai_insights_view(user_id)

        dashboard = SITerminalFullDashboard(
            project_id=stic_config.STIC_PROJECT_ID,
            user_id=user_id,
            user_name=profile.get("user_id", user_id),
            portfolio=portfolio_view,
            ai_insights=ai_view,
            meta={
                "project_title": stic_config.STIC_PROJECT_TITLE,
                "api_endpoint": stic_config.PERSON4_API_URL,
            },
        )
        return dashboard.model_dump()

    def get_tool_definitions(self) -> list[dict]:
        """Returns MCP tool definitions and schemas."""
        return [
            {
                "name": "stic_get_portfolio_intelligence",
                "description": "Retrieve user portfolio holdings, total value, asset allocation, and health gauge.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID (e.g. moderate_001)"}
                    },
                    "required": ["user_id"],
                },
            },
            {
                "name": "stic_get_personalization_context",
                "description": "Evaluate suitability and personalization context for a target stock symbol.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"},
                        "symbol": {"type": "string", "description": "The stock symbol (e.g. RELIANCE.NS)"},
                        "sector": {"type": "string", "default": "Unknown"},
                        "market_cap": {"type": "string", "default": "ANY"},
                        "volatility": {"type": "string", "default": "MEDIUM"},
                    },
                    "required": ["user_id", "symbol"],
                },
            },
            {
                "name": "stic_get_advanced_risk_report",
                "description": "Retrieve quantitative volatility, drawdown, and factor breakdown.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["user_id"],
                },
            },
            {
                "name": "stic_get_investor_behavior_profile",
                "description": "Retrieve trading archetype, risk alignment, and AI market signals.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["user_id"],
                },
            },
            {
                "name": "stic_get_terminal_dashboard_data",
                "description": "Retrieve unified dashboard payload powering all SI Terminal screens.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["user_id"],
                },
            },
        ]
