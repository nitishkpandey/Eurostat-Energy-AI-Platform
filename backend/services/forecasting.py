from __future__ import annotations

from typing import Any

import pandas as pd

from backend.services.models.forecast_utils import run_forecast

from .analytics.common import to_records


def build_forecast_payload(
    dataframe: pd.DataFrame,
    country_code: str,
    indicator_code: str,
    horizon: int,
) -> dict[str, Any]:
    forecast_df, model_used = run_forecast(
        dataframe,
        country=country_code,
        indicator=indicator_code,
        horizon=horizon,
    )
    return {
        "country_code": country_code,
        "indicator_code": indicator_code,
        "horizon": horizon,
        "model_used": model_used,
        "forecast": to_records(forecast_df),
    }
