"""
StIC MCP Server
Exposes unified multi-agent AI, RAG document search, market intelligence,
and portfolio personalization tools for AI agents and LLM consumers.
"""

from typing import Any, Dict, List, Optional
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
    Connects agents cleanly to the unified backend without duplicating business logic.
    """

    def __init__(self, client: Optional[StICPerson4Client] = None):
        self.client = client or StICPerson4Client()
        self.portfolio_adapter = StICPortfolioAdapter(self.client)
        self.ai_insights_adapter = StICAIInsightsAdapter(self.client)

    # ============================================================
    # TOOL 1: Multi-Agent AI Analysis (Person 1)
    # ============================================================
    def stic_run_multi_agent_analysis(
        self,
        user_id: str,
        symbol: str,
        analysis_type: str = "full",
        include_rag: bool = True,
        include_news: bool = True,
    ) -> Dict[str, Any]:
        """
        MCP Tool: Trigger 5-agent parallel financial AI analysis (Technical, Fundamental,
        Sentiment, Risk, Synthesis) tailored to the specified user and ticker.
        """
        return self.client.run_multi_agent_analysis(
            user_id=user_id,
            symbol=symbol,
            analysis_type=analysis_type,
            include_rag=include_rag,
            include_news=include_news,
        )

    # ============================================================
    # TOOL 2: Financial RAG Search (Person 2)
    # ============================================================
    def stic_query_financial_rag(
        self,
        query: str,
        symbol: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        MCP Tool: Perform semantic search over corporate filings, quarterly results, and
        financial reports with exact document citations.
        """
        return self.client.query_rag(query=query, symbol=symbol, top_k=top_k)

    # ============================================================
    # TOOL 3: Market Data Quotes (Person 2)
    # ============================================================
    def stic_get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve live or cached pricing quote, day range, volume, and change percentage.
        """
        return self.client.get_market_data(symbol=symbol)

    # ============================================================
    # TOOL 4: Technical Indicators (Person 2)
    # ============================================================
    def stic_get_market_indicators(self, symbol: str, period: str = "3mo") -> Dict[str, Any]:
        """
        MCP Tool: Retrieve calculated technical indicators (RSI, MACD, Moving Averages, Volatility, Momentum).
        """
        return self.client.get_market_indicators(symbol=symbol, period=period)

    # ============================================================
    # TOOL 5: Financial News & Sentiment (Person 2)
    # ============================================================
    def stic_get_news(self, symbol: str) -> Dict[str, Any]:
        """
        MCP Tool: Fetch parsed financial news headlines and sentiment scores for a stock symbol.
        """
        return self.client.get_news(symbol=symbol)

    # ============================================================
    # TOOL 6: Portfolio Intelligence (Person 4)
    # ============================================================
    def stic_get_portfolio_intelligence(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve formatted portfolio intelligence, holdings, sector allocation,
        and health metrics for a given user.
        """
        portfolio_view = self.portfolio_adapter.get_terminal_portfolio_view(user_id)
        return portfolio_view.model_dump()

    # ============================================================
    # TOOL 7: User Behavior & Investor Profile (Person 4)
    # ============================================================
    def stic_get_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve user trading frequency, turnover, holding style, and behavior flags.
        """
        return self.client.get_behavior(user_id)

    def stic_get_investor_behavior_profile(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve investor trading archetype, declared vs observed risk alignment,
        and synthesized AI insight signals.
        """
        ai_view = self.ai_insights_adapter.get_terminal_ai_insights_view(user_id)
        return ai_view.model_dump()

    # ============================================================
    # TOOL 8: Advanced Risk Analytics (Person 4)
    # ============================================================
    def stic_get_advanced_risk(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve quantitative risk metrics including annualized volatility,
        Parametric Value at Risk (VaR), CVaR, and portfolio stress factor breakdowns.
        """
        return self.client.get_advanced_risk(user_id)

    def stic_get_advanced_risk_report(self, user_id: str) -> Dict[str, Any]:
        """Backward-compatible alias for advanced risk report."""
        return self.stic_get_advanced_risk(user_id)

    # ============================================================
    # TOOL 9: Personalization Suitability Context (Person 4)
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
    # TOOL 10: Consolidated Terminal Dashboard Aggregation
    # ============================================================
    def stic_get_terminal_dashboard_data(
        self,
        user_id: str,
        symbol: Optional[str] = "RELIANCE.NS",
    ) -> Dict[str, Any]:
        """
        MCP Tool: Retrieve unified dashboard payload powering the SI Terminal Intelligence Platform.
        Aggregates profile, portfolio, risk, market quote, indicators, and personalization context.
        """
        profile = self.client.get_profile(user_id)
        portfolio_view = self.portfolio_adapter.get_terminal_portfolio_view(user_id)
        ai_view = self.ai_insights_adapter.get_terminal_ai_insights_view(user_id)

        market_data = {}
        indicators = {}
        suitability = {}
        if symbol:
            try:
                market_data = self.client.get_market_data(symbol)
                indicators = self.client.get_market_indicators(symbol)
                suitability = self.client.get_personalization_context(user_id=user_id, symbol=symbol)
            except Exception:
                pass

        dashboard = SITerminalFullDashboard(
            project_id=stic_config.STIC_PROJECT_ID,
            user_id=user_id,
            user_name=profile.get("user_id", user_id),
            portfolio=portfolio_view,
            ai_insights=ai_view,
            meta={
                "project_title": stic_config.STIC_PROJECT_TITLE,
                "api_endpoint": self.client.base_url,
                "target_symbol": symbol,
                "market_data": market_data,
                "indicators": indicators,
                "suitability": suitability,
            },
        )
        return dashboard.model_dump()

    # ============================================================
    # PRESERVED CONVENIENCE TOOLS
    # ============================================================
    def stic_get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """MCP Tool: Fetch user risk preferences, declared risk capacity, and investment horizon."""
        return self.client.get_profile(user_id)

    def stic_get_user_holdings(self, user_id: str) -> Dict[str, Any]:
        """MCP Tool: Fetch raw portfolio holdings, cash balances, and positions."""
        return self.client.get_portfolio(user_id)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns MCP tool definitions and schemas for LLMs and agent tool dispatchers."""
        return [
            {
                "name": "stic_run_multi_agent_analysis",
                "description": "Trigger automated 5-agent parallel AI investment analysis (Technical, Fundamental, Sentiment, Risk, Synthesis).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID (e.g. moderate_001)"},
                        "symbol": {"type": "string", "description": "Stock ticker (e.g. RELIANCE.NS, TCS)"},
                        "analysis_type": {"type": "string", "default": "full"},
                        "include_rag": {"type": "boolean", "default": True},
                        "include_news": {"type": "boolean", "default": True},
                    },
                    "required": ["user_id", "symbol"],
                },
            },
            {
                "name": "stic_query_financial_rag",
                "description": "Perform semantic similarity search over corporate filings and financial reports with citations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Financial search query"},
                        "symbol": {"type": "string", "description": "Optional ticker filter"},
                        "top_k": {"type": "integer", "default": 5},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "stic_get_market_data",
                "description": "Retrieve live or cached market quote, day range, volume, and change percentage.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker (e.g. RELIANCE.NS)"}
                    },
                    "required": ["symbol"],
                },
            },
            {
                "name": "stic_get_market_indicators",
                "description": "Retrieve computed technical indicators (RSI, MACD, EMA20, EMA50, Volatility, Momentum).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker"},
                        "period": {"type": "string", "default": "3mo"},
                    },
                    "required": ["symbol"],
                },
            },
            {
                "name": "stic_get_news",
                "description": "Retrieve financial news headlines and rule-based sentiment scores for a stock symbol.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker"}
                    },
                    "required": ["symbol"],
                },
            },
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
                "name": "stic_get_user_behavior",
                "description": "Retrieve trading frequency, turnover, holding style, and behavior risk flags.",
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
                "description": "Retrieve investor trading archetype, declared vs observed risk alignment, and AI market signals.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["user_id"],
                },
            },
            {
                "name": "stic_get_advanced_risk",
                "description": "Retrieve quantitative volatility, Value at Risk (VaR), and risk factor breakdown.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["user_id"],
                },
            },
            {
                "name": "stic_get_advanced_risk_report",
                "description": "Retrieve quantitative volatility, drawdown, and factor breakdown (alias for stic_get_advanced_risk).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"}
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
                        "symbol": {"type": "string", "description": "Stock symbol (e.g. RELIANCE.NS)"},
                        "sector": {"type": "string", "default": "Unknown"},
                        "market_cap": {"type": "string", "default": "ANY"},
                        "volatility": {"type": "string", "default": "MEDIUM"},
                    },
                    "required": ["user_id", "symbol"],
                },
            },
            {
                "name": "stic_get_terminal_dashboard_data",
                "description": "Retrieve consolidated dashboard payload powering all SI Terminal screens.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"},
                        "symbol": {"type": "string", "description": "Optional target ticker", "default": "RELIANCE.NS"},
                    },
                    "required": ["user_id"],
                },
            },
            {
                "name": "stic_get_user_profile",
                "description": "Fetch investor profile, declared risk capacity, and investment horizon.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["user_id"],
                },
            },
            {
                "name": "stic_get_user_holdings",
                "description": "Fetch portfolio holdings, cash balances, and positions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["user_id"],
                },
            },
        ]
