from __future__ import annotations

from functools import lru_cache

import pandas as pd

from backend.core.database import load_observations_df


@lru_cache(maxsize=1)
def _cached_observations() -> pd.DataFrame:
    df = load_observations_df()
    if df.empty:
        return df

    required_columns = {
        "year",
        "geo",
        "country_name",
        "indicator",
        "indicator_label",
        "value",
        "unit_label",
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df.copy()


def clear_observations_cache() -> None:
    _cached_observations.cache_clear()


def get_observations(refresh: bool = False) -> pd.DataFrame:
    if refresh:
        clear_observations_cache()
    return _cached_observations()


def resolve_year_bounds(
    df: pd.DataFrame,
    start_year: int | None,
    end_year: int | None,
) -> tuple[int, int]:
    if df.empty:
        raise ValueError("Dataset is empty.")

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())

    resolved_start = start_year if start_year is not None else min_year
    resolved_end = end_year if end_year is not None else max_year

    if resolved_start > resolved_end:
        raise ValueError("start_year must be less than or equal to end_year")

    return resolved_start, resolved_end
