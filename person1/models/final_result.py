from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict
from datetime import datetime

from models.agent_result import AgentResult


class PerformanceMetrics(BaseModel):
    total_latency_ms: int = 0
    technical_latency_ms: int = 0
    fundamental_latency_ms: int = 0
    sentiment_latency_ms: int = 0
    risk_latency_ms: int = 0
    slowest_agent_ms: int = 0


class FinalResult(BaseModel):
    """
    Final synthesized recommendation returned to frontend.
    """

    model_config = ConfigDict(populate_by_name=True)

    symbol: str

    overall_signal: str

    confidence: float = Field(..., ge=0, le=1)

    summary: str

    key_reasons: List[str] = Field(default_factory=list)

    risks: List[str] = Field(default_factory=list)

    sources: List[str] = Field(default_factory=list)

    agents: Dict[str, AgentResult] = Field(default_factory=dict)

    metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)

    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())