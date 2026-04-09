from __future__ import annotations

import json
import os
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.api.schemas import AskRequest, ForecastRequest
from backend.api.services import build_explorer, build_metadata, build_overview
from backend.core.database import load_observations_df
from backend.llm_app.chatbot import answer_question
from backend.ml.forecast_utils import run_forecast


@lru_cache(maxsize=1)
def _cached_observations() -> pd.DataFrame:
    return load_observations_df()


def get_observations(refresh: bool = False) -> pd.DataFrame:
    if refresh:
        _cached_observations.cache_clear()
    return _cached_observations()


def _resolve_year_bounds(df: pd.DataFrame, start_year: int | None, end_year: int | None) -> tuple[int, int]:
    if df.empty:
        raise HTTPException(status_code=503, detail="No observations found. Run ETL first.")

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    resolved_start = start_year or min_year
    resolved_end = end_year or max_year

    if resolved_start > resolved_end:
        raise HTTPException(status_code=400, detail="start_year must be <= end_year")

    return resolved_start, resolved_end


app = FastAPI(
    title="Eurostat Energy API",
    version="2.0.0",
    description="Analytics, forecasting, and AI endpoints for the React frontend.",
)

allowed_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/cache/refresh")
def refresh_cache() -> dict[str, str]:
    _cached_observations.cache_clear()
    return {"status": "cache_cleared"}


@app.get("/api/metadata")
def metadata(refresh: bool = Query(default=False)) -> dict:
    df = get_observations(refresh=refresh)
    return build_metadata(df)


@app.get("/api/overview")
def overview(
    start_year: int | None = Query(default=None, ge=1900),
    end_year: int | None = Query(default=None, ge=1900),
    refresh: bool = Query(default=False),
) -> dict:
    df = get_observations(refresh=refresh)
    s_year, e_year = _resolve_year_bounds(df, start_year, end_year)
    return build_overview(df, s_year, e_year)


@app.get("/api/explorer")
def explorer(
    country_code: str = Query(..., min_length=2),
    indicator_code: str = Query(..., min_length=1),
    start_year: int | None = Query(default=None, ge=1900),
    end_year: int | None = Query(default=None, ge=1900),
    refresh: bool = Query(default=False),
) -> dict:
    df = get_observations(refresh=refresh)
    s_year, e_year = _resolve_year_bounds(df, start_year, end_year)
    return build_explorer(df, country_code, indicator_code, s_year, e_year)


@app.post("/api/forecast")
def forecast(payload: ForecastRequest, refresh: bool = Query(default=False)) -> dict:
    df = get_observations(refresh=refresh)
    if df.empty:
        raise HTTPException(status_code=503, detail="No observations found. Run ETL first.")

    forecast_df, model_used = run_forecast(
        df,
        payload.country_code,
        payload.indicator_code,
        horizon=payload.horizon,
    )

    forecast_records = []
    if not forecast_df.empty:
        forecast_records = json.loads(forecast_df.to_json(orient="records"))

    return {
        "country_code": payload.country_code,
        "indicator_code": payload.indicator_code,
        "horizon": payload.horizon,
        "model_used": model_used,
        "forecast": forecast_records,
    }


@app.post("/api/ai/ask")
def ask_ai(payload: AskRequest) -> dict:
    result = answer_question(payload.question)
    return result
