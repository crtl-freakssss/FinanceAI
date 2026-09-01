from enum import Enum
from typing import Optional
from pydantic import BaseModel
from models.preferences import UserPreferences
from models.constraints import InvestmentConstraints


class RiskTolerance(str, Enum):
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"


class RiskCapacity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InvestmentHorizon(str, Enum):
    SHORT_TERM = "SHORT_TERM"
    MEDIUM_TERM = "MEDIUM_TERM"
    LONG_TERM = "LONG_TERM"


class UserProfile(BaseModel):
    user_id: str
    name: str = ""
    risk_tolerance: str = "MODERATE"
    risk_capacity: str = "MEDIUM"
    investment_horizon: str = "MEDIUM_TERM"
    investor_style: str = "BALANCED"
    capital: float = 0.0
    preferences: Optional[UserPreferences] = None
    constraints: Optional[InvestmentConstraints] = None

    @property
    def max_position_percent(self) -> float:
        if self.constraints and getattr(self.constraints, "max_single_position_pct", None) is not None:
            return float(self.constraints.max_single_position_pct)
        return 100.0

    @property
    def max_sector_percent(self) -> float:
        if self.constraints and getattr(self.constraints, "max_sector_exposure_pct", None) is not None:
            return float(self.constraints.max_sector_exposure_pct)
        return 100.0
