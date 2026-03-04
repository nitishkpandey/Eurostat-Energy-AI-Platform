"""Forecast router – runs ML models and returns predictions."""
from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from api.dependencies import get_db_engine
from api.schemas import ForecastPoint, ForecastResponse
from ml.forecast_utils import run_forecast

router = APIRouter(prefix="/forecast", tags=["forecast"])


def _load_df() -> pd.DataFrame:
    """Load observations from the database and enrich with year/geo/indicator columns."""
    engine = get_db_engine()
    try:
        df = pd.read_sql("SELECT * FROM observations", engine)
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return df

    df["year"] = pd.to_datetime(df["time"]).dt.year.astype(int)
    df["geo"] = df["country_code"]
    df["indicator"] = df["indicator_code"]
    return df


@router.get("/", response_model=ForecastResponse)
def get_forecast(
    country: str = Query(..., description="Country code, e.g. DE"),
    indicator: str = Query(..., description="Indicator code, e.g. GEP"),
    horizon: int = Query(default=5, ge=1, le=20, description="Forecast horizon in years"),
) -> ForecastResponse:
    """Run an ML forecast for the given country/indicator and return results."""
    df = _load_df()
    if df.empty:
        raise HTTPException(status_code=503, detail="No data available. Run the ETL pipeline first.")

    forecast_df, model_used = run_forecast(df, country, indicator, horizon=horizon)

    if forecast_df.empty:
        raise HTTPException(
            status_code=422,
            detail=f"Insufficient data to forecast {indicator} for {country}.",
        )

    points: list[ForecastPoint] = [
        ForecastPoint(year=int(row["year"]), value=float(row["value"]), type=str(row["type"]))
        for _, row in forecast_df.iterrows()
    ]

    return ForecastResponse(model_used=model_used, data=points)
