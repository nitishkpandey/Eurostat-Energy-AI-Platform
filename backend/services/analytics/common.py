from __future__ import annotations

import json
from typing import Any

import pandas as pd


def to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    return json.loads(df.to_json(orient="records", date_format="iso"))


def filter_by_year(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    if df.empty:
        return df
    return df[df["year"].between(start_year, end_year)]
