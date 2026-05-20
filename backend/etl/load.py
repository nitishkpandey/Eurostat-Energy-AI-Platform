"""ETL load module.

Uses backend.core.database for all DB access — single source of truth.
"""
from __future__ import annotations

import logging
import time

import pandas as pd
from sqlalchemy import text

from backend.core.database import get_db_url, get_engine, is_sqlite

logger = logging.getLogger(__name__)


def wait_for_db(max_retries: int = 20, delay: int = 5) -> None:
    """Block until the database accepts connections.

    Returns immediately for SQLite (serverless). For PostgreSQL, retries
    with exponential back-off using psycopg2 directly.
    """
    url = get_db_url()

    if url.startswith("sqlite"):
        logger.info("Using SQLite — no startup wait required.")
        return

    import urllib.parse

    import psycopg2  # lazy import: only needed for PostgreSQL

    raw = url.replace("postgresql+psycopg2://", "postgresql://")
    parsed = urllib.parse.urlparse(raw)

    for attempt in range(1, max_retries + 1):
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
            return
        except psycopg2.OperationalError:
            logger.warning("Waiting for PostgreSQL… attempt %d/%d", attempt, max_retries)
            time.sleep(delay)

    raise RuntimeError("Could not connect to PostgreSQL after %d attempts." % max_retries)


def init_db(engine, mode: str) -> None:
    """Initialise the observations table.

    Modes:
        full-refresh  – drop and recreate the table
        truncate      – keep schema, delete all rows
        append        – create if not exists, keep existing rows
    """
    pk = "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite(engine) else "SERIAL PRIMARY KEY"

    create_sql = f"""
        CREATE TABLE IF NOT EXISTS observations (
            id               {pk},
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
            conn.execute(text(create_sql))
            logger.info("Dropped and recreated 'observations' table.")
        elif mode == "truncate":
            stmt = "DELETE FROM observations" if is_sqlite(engine) else "TRUNCATE TABLE observations"
            conn.execute(text(stmt))
            logger.info("Truncated 'observations' table.")
        elif mode == "append":
            conn.execute(text(create_sql))
            logger.info("Ensured 'observations' table exists (append mode).")


def load_data_to_db(df: pd.DataFrame, engine) -> None:
    """Load a DataFrame into the observations table."""
    if df.empty:
        logger.info("No data to load — skipping.")
        return

    df.to_sql("observations", engine, if_exists="append", index=False)
    logger.info("Loaded %d rows to 'observations' table.", len(df))
