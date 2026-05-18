"""ETL load module.

Uses backend.core.database for all DB access — single source of truth.
"""
from __future__ import annotations

import logging
import time

import psycopg2
from sqlalchemy import text

import pandas as pd

from backend.core.database import get_db_url, get_engine

logger = logging.getLogger(__name__)


def wait_for_db(max_retries: int = 20, delay: int = 5) -> None:
    """Wait for the PostgreSQL database to become available."""
    import urllib.parse

    url = get_db_url()
    # Parse from SQLAlchemy URL: postgresql+psycopg2://user:pass@host:port/db
    # Strip driver prefix so psycopg2 can parse it
    raw = url.replace("postgresql+psycopg2://", "postgresql://")
    parsed = urllib.parse.urlparse(raw)

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname=parsed.path.lstrip("/"),
                user=parsed.username,
                password=parsed.password,
                host=parsed.hostname,
                port=parsed.port or 5432,
            )
            conn.close()
            logger.info("PostgreSQL is available.")
            print("PostgreSQL is available.")
            return
        except psycopg2.OperationalError:
            logger.warning("Waiting for PostgreSQL... attempt %d", i + 1)
            print(f"Waiting for PostgreSQL... attempt {i + 1}")
            time.sleep(delay)

    raise RuntimeError("Could not connect to PostgreSQL after multiple attempts.")


def init_db(engine, mode: str) -> None:
    """Initialise the observations table based on the chosen mode.

    Modes:
        full-refresh  – drop and recreate the table
        truncate      – keep schema, delete all rows
        append        – create if not exists, keep existing rows
    """
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS observations (
            id               SERIAL PRIMARY KEY,
            dataset_code     TEXT,
            country_code     TEXT,
            country_name     TEXT,
            indicator_code   TEXT,
            indicator_label  TEXT,
            unit_code        TEXT,
            unit_label       TEXT,
            time             DATE,
            value            FLOAT,
            load_timestamp   TIMESTAMP
        );
    """

    with engine.begin() as conn:
        if mode == "full-refresh":
            conn.execute(text("DROP TABLE IF EXISTS observations"))
            conn.execute(text(create_table_sql))
            logger.info("Dropped and recreated 'observations' table.")
            print("Dropped and recreated 'observations' table.")
        elif mode == "truncate":
            conn.execute(text("TRUNCATE TABLE observations"))
            logger.info("Truncated 'observations' table.")
            print("Truncated 'observations' table.")
        elif mode == "append":
            conn.execute(text(create_table_sql))
            logger.info("Append mode: ensured 'observations' table exists.")
            print("Append mode: ensured 'observations' table exists.")


def load_data_to_db(df: pd.DataFrame, engine) -> None:
    """Load a DataFrame into the observations table."""
    if df.empty:
        logger.info("No data to load.")
        print("No data to load.")
        return

    df.to_sql("observations", engine, if_exists="append", index=False)
    logger.info("Loaded %d rows to 'observations' table.", len(df))
    print(f"Loaded {len(df)} rows to 'observations' table.")
