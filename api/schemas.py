"""Pydantic response schemas for the API."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ObservationRow(BaseModel):
    year: int
    country_code: str
    country_name: str
    indicator_code: str
    indicator_label: str
    unit_label: str
    value: float


class DataResponse(BaseModel):
    records: List[ObservationRow]
    total: int
    min_year: int
    max_year: int
    countries: List[str]
    indicators: List[str]


class ForecastPoint(BaseModel):
    year: int
    value: float
    type: str  # 'historical' | 'forecast'


class ForecastResponse(BaseModel):
    model_used: str
    data: List[ForecastPoint]


class InsightResponse(BaseModel):
    answer: str
    mode: str


class MetricsResponse(BaseModel):
    total_gep_latest: float
    top_producer_name: str
    top_producer_value: float
    avg_gep: float
    countries_reporting: int
    gep_change_pct: float
    latest_year: int
