"""Shared FastAPI dependencies."""
from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@lru_cache(maxsize=1)
def get_db_engine() -> Engine:
    """Return a cached SQLAlchemy engine using environment variables."""
    db_user = os.getenv("DB_USER", "energy_user")
    db_pass = os.getenv("DB_PASS", "energy_pass")
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "energy")
    url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url, pool_pre_ping=True)
