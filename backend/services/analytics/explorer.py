from __future__ import annotations

from typing import Any

import pandas as pd

from .common import filter_by_year, to_records


def build_explorer(
    df: pd.DataFrame,
    country_code: str,
    indicator_code: str,
    start_year: int,
    end_year: int,
) -> dict[str, Any]:
    filtered = filter_by_year(df, start_year, end_year)

    subset = filtered[(filtered["geo"] == country_code) & (filtered["indicator"] == indicator_code)]

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
        "time_series": to_records(time_series),
        "top_countries": to_records(top_countries),
        "raw_data": to_records(raw_data),
    }
