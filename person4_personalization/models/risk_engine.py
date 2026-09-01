from typing import List, Optional

from pydantic import BaseModel, Field


class RiskMetric(BaseModel):
    value: Optional[float] = None
    status: str = "calculated"
    score: float = Field(default=0.0, ge=0.0, le=100.0)


class VolatilityRisk(RiskMetric):
    annualized_volatility: Optional[float] = None


class DrawdownRisk(RiskMetric):
    maximum_drawdown: Optional[float] = None


class LiquidityRisk(RiskMetric):
    liquidity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )


class SectorRisk(BaseModel):
    sector: str
    exposure_percent: float = Field(
        ge=0.0,
        le=100.0,
    )
    limit_percent: Optional[float] = None
    breach: bool = False


class RiskFactor(BaseModel):
    code: str
    severity: str
    message: str


class RiskDataQuality(BaseModel):
    volatility: str = "unavailable"
    drawdown: str = "unavailable"
    liquidity: str = "unavailable"
    overall: str = "complete"


class AdvancedRiskAssessment(BaseModel):
    user_id: str

    risk_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    risk_level: str

    volatility: VolatilityRisk
    drawdown: DrawdownRisk
    liquidity: LiquidityRisk

    concentration_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    diversification_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    sector_risk: List[SectorRisk] = Field(
        default_factory=list
    )

    risk_factors: List[RiskFactor] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(
        default_factory=list
    )

    data_quality: RiskDataQuality