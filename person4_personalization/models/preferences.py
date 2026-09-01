from typing import List
from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    preferred_sectors: List[str] = Field(default_factory=list)
    excluded_sectors: List[str] = Field(default_factory=list)
    esg_only: bool = False
