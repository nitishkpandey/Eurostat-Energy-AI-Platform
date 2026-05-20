"""Pydantic request schemas for the API layer."""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=24)
    indicator_code: str = Field(..., min_length=1, max_length=64)
    horizon: int = Field(default=5, ge=1, le=20)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
