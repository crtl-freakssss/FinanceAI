from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PersonalizationContext(BaseModel):
    user_id: str
    risk_tolerance: str
    risk_capacity: str
    investment_horizon: str
    investor_style: str
    capital: float
    portfolio: Optional[Dict[str, Any]] = None
    portfolio_snapshot: Optional[Dict[str, Any]] = None
    symbol: str
    sector: str
    market_cap: str = "ANY"
    volatility: str = "MEDIUM"
    position_exposure_percent: float = 0.0
    risk_score: float = 50.0
    risk_level: str = "MEDIUM"
    suitability_score: float = 50.0
    suitability: str = "SUITABLE"
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    constraint_breaches: List[str] = Field(default_factory=list)
