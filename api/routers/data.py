"""Data router – exposes energy observations from PostgreSQL."""
from __future__ import annotations

from typing import List

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import ProgrammingError

from api.dependencies import get_db_engine
from api.schemas import DataResponse, MetricsResponse, ObservationRow

router = APIRouter(prefix="/data", tags=["data"])


def _load_df() -> pd.DataFrame:
    """Load observations from the database and enrich with year/geo/indicator columns."""
    engine = get_db_engine()
    try:
        df = pd.read_sql("SELECT * FROM observations", engine)
    except ProgrammingError:
        return pd.DataFrame()

    if df.empty:
        return df

    df["year"] = pd.to_datetime(df["time"]).dt.year.astype(int)
    df["geo"] = df["country_code"]
    df["indicator"] = df["indicator_code"]
    return df


@router.get("/", response_model=DataResponse)
def get_data(
    min_year: int = Query(default=0, description="Minimum year (inclusive)"),
    max_year: int = Query(default=9999, description="Maximum year (inclusive)"),
) -> DataResponse:
    """Return all observations filtered by year range."""
    df = _load_df()
    if df.empty:
        raise HTTPException(status_code=503, detail="No data available. Run the ETL pipeline first.")

    filtered = df[df["year"].between(min_year, max_year)]

    records: List[ObservationRow] = [
        ObservationRow(
            year=int(row["year"]),
            country_code=str(row["country_code"]),
            country_name=str(row["country_name"]),
            indicator_code=str(row["indicator_code"]),
            indicator_label=str(row.get("indicator_label") or row["indicator_code"]),
            unit_label=str(row.get("unit_label") or ""),
            value=float(row["value"]),
        )
        for _, row in filtered.iterrows()
    ]

    return DataResponse(
        records=records,
        total=len(records),
        min_year=int(df["year"].min()),
        max_year=int(df["year"].max()),
        countries=sorted(df["country_code"].dropna().unique().tolist()),
        indicators=sorted(df["indicator_code"].dropna().unique().tolist()),
    )


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics() -> MetricsResponse:
    """Return KPI metrics for the overview dashboard."""
    df = _load_df()
    if df.empty:
        raise HTTPException(status_code=503, detail="No data available.")

    latest_year = int(df["year"].max())
    prev_year = latest_year - 1

    gep_latest = df[(df["year"] == latest_year) & (df["indicator"] == "GEP")]
    gep_prev = df[(df["year"] == prev_year) & (df["indicator"] == "GEP")]

    total_gep = float(gep_latest["value"].sum())
    prev_gep = float(gep_prev["value"].sum())
    gep_change = ((total_gep - prev_gep) / prev_gep * 100) if prev_gep > 0 else 0.0

    top_row = gep_latest.nlargest(1, "value")
    top_name = str(top_row.iloc[0]["country_name"]) if not top_row.empty else "N/A"
    top_val = float(top_row.iloc[0]["value"]) if not top_row.empty else 0.0

    avg_gep = float(gep_latest["value"].mean()) if not gep_latest.empty else 0.0
    countries_reporting = int(gep_latest["geo"].nunique())

    return MetricsResponse(
        total_gep_latest=total_gep,
        top_producer_name=top_name,
        top_producer_value=top_val,
        avg_gep=avg_gep,
        countries_reporting=countries_reporting,
        gep_change_pct=gep_change,
        latest_year=latest_year,
    )
