from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.api.schemas import AskRequest, ForecastRequest
from backend.services import (
    ask_question,
    build_forecast_payload,
    clear_observations_cache,
    get_observations,
    resolve_year_bounds,
)
from backend.services.analytics import build_explorer, build_metadata, build_overview


app = FastAPI(
    title="Eurostat Energy API",
    version="2.0.0",
    description="Analytics, forecasting, and AI endpoints for the React frontend.",
)


def _load_observations_or_503(refresh: bool):
    try:
        return get_observations(refresh=refresh)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _resolve_bounds_or_4xx(df, start_year: int | None, end_year: int | None) -> tuple[int, int]:
    try:
        return resolve_year_bounds(df, start_year, end_year)
    except ValueError as exc:
        status_code = 503 if "empty" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

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
    clear_observations_cache()
    return {"status": "cache_cleared"}


@app.get("/api/metadata")
def metadata(refresh: bool = Query(default=False)) -> dict:
    df = _load_observations_or_503(refresh=refresh)
    return build_metadata(df)


@app.get("/api/overview")
def overview(
    start_year: int | None = Query(default=None, ge=1900),
    end_year: int | None = Query(default=None, ge=1900),
    refresh: bool = Query(default=False),
) -> dict:
    df = _load_observations_or_503(refresh=refresh)
    s_year, e_year = _resolve_bounds_or_4xx(df, start_year, end_year)
    return build_overview(df, s_year, e_year)


@app.get("/api/explorer")
def explorer(
    country_code: str = Query(..., min_length=2),
    indicator_code: str = Query(..., min_length=1),
    start_year: int | None = Query(default=None, ge=1900),
    end_year: int | None = Query(default=None, ge=1900),
    refresh: bool = Query(default=False),
) -> dict:
    df = _load_observations_or_503(refresh=refresh)
    s_year, e_year = _resolve_bounds_or_4xx(df, start_year, end_year)
    return build_explorer(df, country_code, indicator_code, s_year, e_year)


@app.post("/api/forecast")
def forecast(payload: ForecastRequest, refresh: bool = Query(default=False)) -> dict:
    df = _load_observations_or_503(refresh=refresh)

    return build_forecast_payload(
        dataframe=df,
        country_code=payload.country_code,
        indicator_code=payload.indicator_code,
        horizon=payload.horizon,
    )


@app.post("/api/ai/ask")
def ask_ai(payload: AskRequest) -> dict:
    return ask_question(payload.question)
