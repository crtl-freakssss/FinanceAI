from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    transaction_id: str
    symbol: str
    transaction_type: str
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    date: str
    sector: Optional[str] = None


class TradingStatistics(BaseModel):
    total_transactions: int = Field(ge=0)
    buy_transactions: int = Field(ge=0)
    sell_transactions: int = Field(ge=0)

    total_buy_value: float = Field(ge=0)
    total_sell_value: float = Field(ge=0)

    average_transaction_value: float = Field(ge=0)

    trading_frequency: str
    turnover_level: str


class HoldingPeriodStatistics(BaseModel):
    average_holding_days: Optional[float] = None
    shortest_holding_days: Optional[int] = None
    longest_holding_days: Optional[int] = None

    holding_style: str


class TradingPerformance(BaseModel):
    completed_trades: int = Field(ge=0)
    winning_trades: int = Field(ge=0)
    losing_trades: int = Field(ge=0)

    win_rate: Optional[float] = None

    realized_profit: float = 0.0
    realized_loss: float = 0.0

    profit_factor: Optional[float] = None


class BehaviourFlag(BaseModel):
    code: str
    severity: str
    message: str


class BehaviourDataQuality(BaseModel):
    transaction_history: str
    performance_history: str
    holding_period_history: str
    overall: str


class BehaviourAssessment(BaseModel):
    user_id: str

    behaviour_score: float = Field(
        ge=0,
        le=100,
    )

    behaviour_risk_level: str

    trading: TradingStatistics

    holding_period: HoldingPeriodStatistics

    performance: TradingPerformance

    consistency_score: float = Field(
        ge=0,
        le=100,
    )

    loss_tolerance: str

    investor_archetype: str

    behaviour_flags: List[BehaviourFlag] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(
        default_factory=list
    )

    data_quality: BehaviourDataQuality


class InvestorProfileAssessment(BaseModel):
    user_id: str

    declared_risk_profile: str
    observed_risk_profile: str

    investor_type: str

    alignment: str

    behaviour_score: float = Field(
        ge=0,
        le=100,
    )

    profile_confidence: float = Field(
        ge=0,
        le=100,
    )

    recommendations: List[str] = Field(
        default_factory=list
    )

    behaviour_flags: List[BehaviourFlag] = Field(
        default_factory=list
    )
