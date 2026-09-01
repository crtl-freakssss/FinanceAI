from pydantic import BaseModel, Field


class AllocationItem(BaseModel):
    name: str
    value: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)


class AllocationResult(BaseModel):
    by_symbol: list[AllocationItem] = Field(
        default_factory=list
    )
    by_sector: list[AllocationItem] = Field(
        default_factory=list
    )


class ConcentrationResult(BaseModel):
    largest_position_percent: float = Field(
        ge=0,
        le=100,
    )

    top_three_position_percent: float = Field(
        ge=0,
        le=100,
    )

    largest_sector_percent: float = Field(
        ge=0,
        le=100,
    )

    concentration_score: float = Field(
        ge=0,
        le=100,
    )

    concentration_level: str


class ExposureResult(BaseModel):
    user_id: str
    symbol: str
    sector: str

    position_value: float = Field(ge=0)

    position_exposure_percent: float = Field(
        ge=0,
        le=100,
    )

    sector_value: float = Field(ge=0)

    sector_exposure_percent: float = Field(
        ge=0,
        le=100,
    )

    max_position_percent: float = Field(
        ge=0,
        le=100,
    )

    max_sector_percent: float = Field(
        ge=0,
        le=100,
    )

    position_breach: bool
    sector_breach: bool


class PortfolioRiskResult(BaseModel):
    risk_score: float = Field(
        ge=0,
        le=100,
    )

    risk_level: str

    concentration_score: float = Field(
        ge=0,
        le=100,
    )

    diversification_score: float = Field(
        ge=0,
        le=100,
    )

    cash_percent: float = Field(
        ge=0,
        le=100,
    )

    warnings: list[str] = Field(
        default_factory=list
    )


class PortfolioHealthResult(BaseModel):
    health_score: float = Field(
        ge=0,
        le=100,
    )

    status: str

    diversification_score: float = Field(
        ge=0,
        le=100,
    )

    concentration_score: float = Field(
        ge=0,
        le=100,
    )

    warnings: list[str] = Field(
        default_factory=list
    )


class PortfolioAnalysis(BaseModel):
    user_id: str

    total_value: float = Field(ge=0)
    holdings_value: float = Field(ge=0)
    cash_value: float = Field(ge=0)

    cash_percent: float = Field(
        ge=0,
        le=100,
    )

    equity_percent: float = Field(
        ge=0,
        le=100,
    )

    allocation: AllocationResult
    concentration: ConcentrationResult
    risk: PortfolioRiskResult
    health: PortfolioHealthResult