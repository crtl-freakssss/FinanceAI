from typing import List
from pydantic import BaseModel, Field


class InvestmentConstraints(BaseModel):
    max_single_position_pct: float = 20.0
    max_sector_exposure_pct: float = 35.0
    excluded_sectors: List[str] = Field(default_factory=list)
    restricted_symbols: List[str] = Field(default_factory=list)
