from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class SuitabilityLevel(str, Enum):
    SUITABLE = "SUITABLE"
    CAUTION = "CAUTION"
    UNSUITABLE = "UNSUITABLE"


class SuitabilityAssessment(BaseModel):
    suitability_score: float
    suitability: str
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    constraint_breaches: List[str] = Field(default_factory=list)
