from __future__ import annotations

from math import sqrt
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def _get_series(data: pd.DataFrame, country: str, indicator: str) -> pd.Series:
    """
    Extract a yearly time series for a given country + indicator.

    Expects columns: geo, indicator, time, value.
    Returns a pandas Series indexed by year.
    """
    df = data[(data["geo"] == country) & (data["indicator"] == indicator)].copy()
    if df.empty:
        return pd.Series(dtype=float)

    df["year"] = pd.to_datetime(df["time"]).dt.year
    # In case multiple records per year: take mean
    series = df.groupby("year")["value"].mean().sort_index()
    return series


def _make_supervised(series: pd.Series, n_lags: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, list]:
    """
    Build lag + rolling feature matrix from a 1D Series.
    """
    df = pd.DataFrame({"year": series.index.astype(int), "value": series.values})

    # Lag features
    for lag in range(1, n_lags + 1):
        df[f"lag{lag}"] = df["value"].shift(lag)

    # Rolling statistics (3-year window)
    df["roll_mean_3"] = df["value"].rolling(window=3).mean()
    df["roll_std_3"] = df["value"].rolling(window=3).std()

    df = df.dropna()
    if df.empty:
        return df, pd.DataFrame(), pd.Series(dtype=float), []

    feature_cols = [c for c in df.columns if c not in ["value"]]
    X = df[feature_cols]
    y = df["value"]
    return df, X, y, feature_cols


def _train_xgb(series: pd.Series, horizon: int = 5, test_size: int = 5):
    """
    Train an XGBoost regressor on lag features and perform
    recursive multi-step forecast.
    """
    base_df, X, y, feature_cols = _make_supervised(series)
    if base_df.empty or len(base_df) <= test_size + 1:
        return None, None, None, "XGBoost (insufficient data)"

    # Train/test split
    X_train, X_test = X.iloc[:-test_size], X.iloc[-test_size:]
    y_train, y_test = y.iloc[:-test_size], y.iloc[-test_size:]

    model = XGBRegressor(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate on last part of history
    y_pred = model.predict(X_test)
    rmse = sqrt(mean_squared_error(y_test, y_pred))

    # Recursive forecast
    history_values = base_df["value"].tolist()
    last_year = int(base_df["year"].iloc[-1])

    future_rows = []

    for step in range(1, horizon + 1):
        year = last_year + step

        # Build feature row based on latest history_values
        feats = {}
        feats["year"] = year

        for lag in range(1, 4):
            if len(history_values) >= lag:
                feats[f"lag{lag}"] = history_values[-lag]
            else:
                feats[f"lag{lag}"] = history_values[-1]

        window_vals = history_values[-3:] if len(history_values) >= 3 else history_values
        feats["roll_mean_3"] = float(np.mean(window_vals))
        feats["roll_std_3"] = float(np.std(window_vals)) if len(window_vals) > 1 else 0.0

        # Order the features as in training
        X_future = np.array([[feats[col] for col in feature_cols]])
        y_future = float(model.predict(X_future)[0])

        history_values.append(y_future)
        future_rows.append({"year": year, "value": y_future})

    history_df = base_df[["year", "value"]].copy()
    future_df = pd.DataFrame(future_rows)
    return history_df, future_df, rmse, "XGBoost"


def _train_es(series: pd.Series, horizon: int = 5, test_size: int = 5):
    """
    Train an Exponential Smoothing model as a simple baseline.
    """
    if len(series) <= test_size + 2:
        return None, None, None, "ExponentialSmoothing (insufficient data)"

    # Split into train/test for evaluation
    train = series.iloc[:-test_size]
    test = series.iloc[-test_size:]

    model = ExponentialSmoothing(train, trend="add", seasonal=None)
    fit = model.fit()

    # Forecast the test range to compute RMSE
    es_test_forecast = fit.forecast(test_size)
    rmse = sqrt(mean_squared_error(test, es_test_forecast))

    # Refit on full series for future horizon
    full_fit = ExponentialSmoothing(series, trend="add", seasonal=None).fit()
    future_forecast = full_fit.forecast(horizon)

    history_df = (
        pd.DataFrame({"year": series.index.astype(int), "value": series.values})
        .sort_values("year")
    )
    future_df = (
        pd.DataFrame({"year": future_forecast.index.astype(int), "value": future_forecast.values})
        .sort_values("year")
    )

    return history_df, future_df, rmse, "ExponentialSmoothing"


def run_forecast(
    data: pd.DataFrame,
    country: str,
    indicator: str,
    horizon: int = 5,
):
    """
    Public API used by Streamlit.

    Parameters
    ----------
    data : DataFrame
        Must include columns: geo, indicator, time, value.
    country : str
        Country code (e.g. 'DE').
    indicator : str
        Indicator code (e.g. 'nrg_cb_e').
    horizon : int
        Number of future years to forecast.

    Returns
    -------
    forecast_df : DataFrame
        Columns: ['year', 'value', 'type'] where type is 'historical' or 'forecast'.
    model_used : str
        Name of the model chosen.
    """
    series = _get_series(data, country, indicator)

    if series.empty or len(series) < 5:
        # Not enough data for meaningful forecasting
        empty_df = pd.DataFrame(columns=["year", "value", "type"])
        return empty_df, "No forecast (insufficient data)"

    test_size = min(5, max(2, len(series) // 3))

    # Train both models
    x_hist, x_future, x_rmse, x_name = _train_xgb(series, horizon=horizon, test_size=test_size)
    es_hist, es_future, es_rmse, es_name = _train_es(series, horizon=horizon, test_size=test_size)

    # Decide which model to use
    candidates = []
    if x_hist is not None and x_future is not None and x_rmse is not None:
        candidates.append(("XGBoost", x_rmse, x_hist, x_future))
    if es_hist is not None and es_future is not None and es_rmse is not None:
        candidates.append(("ExponentialSmoothing", es_rmse, es_hist, es_future))

    if not candidates:
        empty_df = pd.DataFrame(columns=["year", "value", "type"])
        return empty_df, "No forecast (insufficient data)"

    # Choose model with lower RMSE
    candidates.sort(key=lambda tup: tup[1])
    best_name, best_rmse, hist_df, fut_df = candidates[0]

    hist_df = hist_df.copy()
    hist_df["type"] = "historical"

    fut_df = fut_df.copy()
    fut_df["type"] = "forecast"

    forecast_df = pd.concat([hist_df, fut_df], ignore_index=True)
    forecast_df = forecast_df.sort_values("year")

    return forecast_df, best_name