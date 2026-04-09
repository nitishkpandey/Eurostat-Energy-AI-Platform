from __future__ import annotations

import json
from typing import Any

import pandas as pd


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    return json.loads(df.to_json(orient="records", date_format="iso"))


def _filter_year(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    if df.empty:
        return df
    return df[df["year"].between(start_year, end_year)]


def build_metadata(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "min_year": None,
            "max_year": None,
            "countries": [],
            "indicators": [],
            "record_count": 0,
        }

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())

    countries_df = (
        df[["geo", "country_name"]]
        .dropna(subset=["geo"])
        .drop_duplicates()
        .sort_values("geo")
        .rename(columns={"geo": "country_code"})
    )

    indicators = sorted(df["indicator"].dropna().unique().tolist())

    return {
        "min_year": min_year,
        "max_year": max_year,
        "countries": _records(countries_df),
        "indicators": indicators,
        "record_count": int(len(df)),
    }


def build_overview(df: pd.DataFrame, start_year: int, end_year: int) -> dict[str, Any]:
    filtered = _filter_year(df, start_year, end_year)
    if filtered.empty:
        return {
            "latest_year": None,
            "kpis": {
                "latest_gep": 0.0,
                "gep_change_pct": 0.0,
                "top_producer": None,
                "avg_gep": 0.0,
                "countries_reporting": 0,
            },
            "top_producers": [],
            "germany_trend": [],
        }

    latest_year = int(filtered["year"].max())
    prev_year = latest_year - 1

    latest_gep_df = filtered[(filtered["year"] == latest_year) & (filtered["indicator"] == "GEP")]
    prev_gep_df = filtered[(filtered["year"] == prev_year) & (filtered["indicator"] == "GEP")]

    latest_gep = float(latest_gep_df["value"].sum())
    prev_gep = float(prev_gep_df["value"].sum())
    gep_change_pct = ((latest_gep - prev_gep) / prev_gep * 100) if prev_gep > 0 else 0.0

    top_producer = None
    if not latest_gep_df.empty:
        top_row = latest_gep_df.sort_values("value", ascending=False).iloc[0]
        top_producer = {
            "country_code": top_row["geo"],
            "country_name": top_row.get("country_name"),
            "value": float(top_row["value"]),
        }

    top_producers = (
        latest_gep_df.groupby(["geo", "country_name"], dropna=False)["value"]
        .mean()
        .reset_index()
        .sort_values("value", ascending=False)
        .head(10)
        .rename(columns={"geo": "country_code"})
    )

    germany_trend = (
        filtered[(filtered["geo"] == "DE") & (filtered["indicator"] == "GEP")][["year", "value"]]
        .drop_duplicates()
        .sort_values("year")
    )

    return {
        "latest_year": latest_year,
        "kpis": {
            "latest_gep": latest_gep,
            "gep_change_pct": float(gep_change_pct),
            "top_producer": top_producer,
            "avg_gep": float(latest_gep_df["value"].mean()) if not latest_gep_df.empty else 0.0,
            "countries_reporting": int(latest_gep_df["geo"].nunique()) if not latest_gep_df.empty else 0,
        },
        "top_producers": _records(top_producers),
        "germany_trend": _records(germany_trend),
    }


def build_explorer(
    df: pd.DataFrame,
    country_code: str,
    indicator_code: str,
    start_year: int,
    end_year: int,
) -> dict[str, Any]:
    filtered = _filter_year(df, start_year, end_year)

    subset = filtered[
        (filtered["geo"] == country_code) & (filtered["indicator"] == indicator_code)
    ]

    time_series = subset[["year", "value"]].dropna().sort_values("year")

    top_countries = (
        filtered[filtered["indicator"] == indicator_code]
        .groupby(["geo", "country_name"], dropna=False)["value"]
        .mean()
        .reset_index()
        .sort_values("value", ascending=False)
        .head(10)
        .rename(columns={"geo": "country_code"})
    )

    raw_data_cols = [
        "year",
        "country_name",
        "indicator_label",
        "value",
        "unit_label",
    ]
    raw_data = subset[raw_data_cols].sort_values("year", ascending=False)

    return {
        "country_code": country_code,
        "indicator_code": indicator_code,
        "time_series": _records(time_series),
        "top_countries": _records(top_countries),
        "raw_data": _records(raw_data),
    }
