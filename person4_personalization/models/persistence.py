import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class HoldingItem(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    shares: float = Field(..., gt=0)
    price: float = Field(..., ge=0)
    value: Optional[float] = Field(None, ge=0)

    @field_validator("shares", "price", "value", mode="before")
    def validate_finite_number(cls, v):
        if v is not None:
            try:
                num = float(v)
                if math.isnan(num) or math.isinf(num):
                    raise ValueError("Numeric values must be finite numbers.")
                return num
            except (TypeError, ValueError) as e:
                raise ValueError("Invalid number format.")
        return v


class UserCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field("", max_length=200)


class UserResponse(BaseModel):
    user_id: str
    name: str
    created_at: Optional[str] = None


class ProfileCreateOrUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    risk_tolerance: str = Field("MODERATE", max_length=50)
    risk_capacity: str = Field("MEDIUM", max_length=50)
    investment_horizon: str = Field("MEDIUM_TERM", max_length=50)
    investor_style: str = Field("BALANCED", max_length=50)
    capital: float = Field(0.0, ge=0)
    preferences: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None

    @field_validator("capital", mode="before")
    def validate_finite_capital(cls, v):
        if v is not None:
            num = float(v)
            if math.isnan(num) or math.isinf(num):
                raise ValueError("Capital must be a finite number.")
            return num
        return 0.0


class PortfolioCreateOrUpdate(BaseModel):
    total_value: float = Field(0.0, ge=0)
    cash: float = Field(0.0, ge=0)
    holdings: List[Dict[str, Any]] = Field(default_factory=list)

    @field_validator("total_value", "cash", mode="before")
    def validate_finite_values(cls, v):
        if v is not None:
            num = float(v)
            if math.isnan(num) or math.isinf(num):
                raise ValueError("Values must be finite numbers.")
            return num
        return 0.0

    @field_validator("holdings")
    def validate_holdings_items(cls, holdings):
        validated = []
        for h in holdings:
            if isinstance(h, dict):
                # Validate holding structure
                shares = float(h.get("shares", 0))
                price = float(h.get("price", 0))
                if shares <= 0:
                    raise ValueError("Holding shares must be greater than 0.")
                if price < 0:
                    raise ValueError("Holding price cannot be negative.")
                if math.isnan(shares) or math.isinf(shares) or math.isnan(price) or math.isinf(price):
                    raise ValueError("Holding shares and price must be finite numbers.")
                validated.append(h)
            else:
                validated.append(h)
        return validated


class AnalysisSessionCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    symbol: Optional[str] = Field(None, max_length=50)
    analysis_type: str = Field("PERSONALIZATION", max_length=50)
    result_data: Optional[Dict[str, Any]] = None


class AnalysisSessionResponse(BaseModel):
    session_id: str
    user_id: str
    symbol: Optional[str] = None
    analysis_type: str
    result_json: Optional[str] = "{}"
    created_at: Optional[str] = None


class AnalysisLogCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)
    level: str = Field("INFO", max_length=20)
    session_id: Optional[str] = Field(None, max_length=100)
    agent_name: str = Field("person4_personalization", max_length=100)
    details: Optional[Dict[str, Any]] = None


class AnalysisLogResponse(BaseModel):
    id: int
    user_id: str
    session_id: Optional[str] = None
    level: str
    agent_name: str
    message: str
    timestamp: Optional[str] = None
