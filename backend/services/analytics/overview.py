from __future__ import annotations

from typing import Any

import pandas as pd

from .common import filter_by_year, to_records


def build_overview(df: pd.DataFrame, start_year: int, end_year: int) -> dict[str, Any]:
    filtered = filter_by_year(df, start_year, end_year)
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
            "selected_country_code": None,
            "country_trends": {},
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

    top_country_codes = top_producers["country_code"].dropna().astype(str).tolist()

    country_trend_rows = (
        filtered[(filtered["indicator"] == "GEP") & (filtered["geo"].isin(top_country_codes))]
        .groupby(["geo", "year"], dropna=False)["value"]
        .mean()
        .reset_index()
        .sort_values(["geo", "year"])
    )

    country_trends = {
        str(country_code): to_records(country_df[["year", "value"]])
        for country_code, country_df in country_trend_rows.groupby("geo", sort=False)
    }

    selected_country_code = "DE" if "DE" in country_trends else (top_country_codes[0] if top_country_codes else None)

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
        "top_producers": to_records(top_producers),
        "germany_trend": to_records(germany_trend),
        "selected_country_code": selected_country_code,
        "country_trends": country_trends,
    }
