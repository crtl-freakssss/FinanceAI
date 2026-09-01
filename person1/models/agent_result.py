from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Literal
from datetime import datetime


class AgentResult(BaseModel):
    """
    Standard response format for every AI agent.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "agent": "technical",
                "signal": "BUY",
                "confidence": 0.82,
                "reasons": [
                    "RSI indicates bullish momentum",
                    "Price is above EMA20 and EMA50",
                    "MACD crossover is positive"
                ],
                "risks": [
                    "Short-term volatility is elevated"
                ],
                "sources": [
                    "Market Indicators"
                ],
                "metadata": {
                    "rsi": 63,
                    "ema20": 3315,
                    "ema50": 3242,
                    "macd": 1.24
                },
                "latency_ms": 178,
                "timestamp": "2026-09-01T10:15:32.123456"
            }
        }
    )

    agent: Literal["technical", "fundamental", "sentiment", "risk"]

    signal: Literal["BUY", "HOLD", "SELL", "AVOID"]

    confidence: float = Field(..., ge=0, le=1)

    reasons: List[str] = Field(default_factory=list)

    risks: List[str] = Field(default_factory=list)

    sources: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    latency_ms: int = 0

    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())