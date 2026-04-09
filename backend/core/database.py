from __future__ import annotations

import os
from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_db_url() -> str:
    """Build a SQLAlchemy database URL from environment variables."""
    db_user = os.getenv("DB_USER", "energy_user")
    db_pass = os.getenv("DB_PASS", "energy_pass")
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "energy")
    return f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create and cache a SQLAlchemy engine for the observations database."""
    return create_engine(get_db_url())


def normalize_observations(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe columns used across analytics, forecasting, and AI flows."""
    if df.empty:
        return df

    normalized = df.copy()
    if "time" in normalized.columns:
        normalized["time"] = pd.to_datetime(normalized["time"], errors="coerce")
        normalized["year"] = normalized["time"].dt.year

    if "geo" not in normalized.columns and "country_code" in normalized.columns:
        normalized["geo"] = normalized["country_code"]

    if "indicator" not in normalized.columns and "indicator_code" in normalized.columns:
        normalized["indicator"] = normalized["indicator_code"]

    return normalized


def load_observations_df(engine: Engine | None = None) -> pd.DataFrame:
    """Load observations from PostgreSQL and return a normalized dataframe."""
    active_engine = engine or get_engine()
    try:
        df = pd.read_sql("SELECT * FROM observations", active_engine)
    except Exception:
        return pd.DataFrame()

    return normalize_observations(df)
