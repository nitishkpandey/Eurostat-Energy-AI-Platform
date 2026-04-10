from __future__ import annotations

from typing import Any

import pandas as pd

from .common import to_records


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
        "countries": to_records(countries_df),
        "indicators": indicators,
        "record_count": int(len(df)),
    }
