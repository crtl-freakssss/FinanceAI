"""
StIC Data Schemas
Pydantic schemas mapping Person 4 API data to SI Terminal UI and StIC MCP Tool formats.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SITerminalHolding(BaseModel):
    """Holding representation formatted for SI Terminal UI table."""
    symbol: str
    shares: float
    avg_price: float
    current_price: float
    total_value: float
    pnl_amount: float
    pnl_percent: float
    weight_percent: float
    sector: str = "Unknown"


class SITerminalSectorAllocation(BaseModel):
    """Sector allocation percentage for SI Terminal chart."""
    sector: str
    value: float
    percentage: float


class SITerminalPortfolioView(BaseModel):
    """Aggregated portfolio analytics formatted for SI Terminal Portfolio Screen."""
    user_id: str
    total_value: float
    holdings_value: float
    cash_value: float
    risk_level: str
    health_score: float
    health_status: str
    diversification_score: float
    top_holding_symbol: str
    top_holding_percent: float
    sector_breakdown: List[SITerminalSectorAllocation]
    holdings: List[SITerminalHolding]
    warnings: List[str] = Field(default_factory=list)


class SITerminalAIInsightItem(BaseModel):
    """Single AI insight item / signal."""
    title: str
    detail: str
    type: str  # e.g., 'bullish', 'bearish', 'warning', 'info'
    symbol: Optional[str] = None


class SITerminalAIInsightsView(BaseModel):
    """Aggregated intelligence formatted for SI Terminal AI Insights Screen."""
    user_id: str
    investor_type: str
    declared_risk_profile: str
    observed_risk_profile: str
    profile_alignment: str
    sentiment_score: int  # 0 to 100
    sentiment_label: str  # e.g., 'Greed', 'Neutral', 'Fear'
    synthesis_summary: str
    consensus_action: str  # e.g., 'BUY', 'HOLD', 'REBALANCE', 'CAUTION'
    signals: List[SITerminalAIInsightItem] = Field(default_factory=list)
    behavior_flags: List[str] = Field(default_factory=list)


class SITerminalFullDashboard(BaseModel):
    """Unified payload powering the complete SI Terminal Intelligence Platform."""
    project_id: str
    user_id: str
    user_name: str
    portfolio: SITerminalPortfolioView
    ai_insights: SITerminalAIInsightsView
    meta: Dict[str, Any] = Field(default_factory=dict)
