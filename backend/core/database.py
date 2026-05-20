"""Centralised database access layer.

Single source of truth for database connections, queries, and
DataFrame normalisation. Supports both PostgreSQL and SQLite backends
controlled by the DB_TYPE environment variable.
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


# ── Connection helpers ──────────────────────────────────────────────────────


def get_db_url() -> str:
    """Build a SQLAlchemy database URL from environment variables."""
    db_type = os.getenv("DB_TYPE", "postgresql")
    db_name = os.getenv("DB_NAME", "energy")

    if db_type == "sqlite":
        return f"sqlite:///{db_name}.db"

    db_user = os.getenv("DB_USER", "energy_user")
    db_pass = os.getenv("DB_PASS", "energy_pass")
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")
    return f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create and cache a SQLAlchemy engine."""
    return create_engine(get_db_url())


def is_sqlite(engine: Engine | None = None) -> bool:
    """Return True if the active engine targets SQLite."""
    return str((engine or get_engine()).url).startswith("sqlite")


# ── DataFrame helpers ───────────────────────────────────────────────────────


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
    """Load observations from the database and return a normalized dataframe."""
    active_engine = engine or get_engine()
    try:
        with active_engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM observations", conn)
    except Exception as exc:
        logger.error("Failed to load observations: %s", exc)
        return pd.DataFrame()

    return normalize_observations(df)
