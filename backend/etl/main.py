"""ETL pipeline entry point.

Usage:
    uv run python -m backend.etl.main --mode full-refresh
    uv run python -m backend.etl.main --mode append
    uv run python -m backend.etl.main --mode truncate
"""
from __future__ import annotations

import argparse
import logging

import pandas as pd

from backend.core.database import get_engine
from .config import DATASETS
from .extract import fetch_dataset
from .load import init_db, load_data_to_db, wait_for_db
from .transform import transform_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Eurostat Energy ETL pipeline")
    parser.add_argument(
        "--mode",
        choices=["append", "truncate", "full-refresh"],
        default="full-refresh",
        help="Data load mode (default: full-refresh)",
    )
    args = parser.parse_args()

    # --- 1. Database Setup ---
    wait_for_db()
    engine = get_engine()
    init_db(engine, args.mode)

    # --- 2. Extract & Transform ---
    all_dataframes: list[pd.DataFrame] = []

    for dataset_code, config in DATASETS.items():
        logger.info("Processing dataset: %s", dataset_code)
        print(f"Processing dataset: {dataset_code}...")

        raw_data = fetch_dataset(dataset_code, config["url"])
        if not raw_data:
            logger.warning("Skipping %s — no data returned.", dataset_code)
            continue

        df = transform_dataset(dataset_code, raw_data, config["indicators"])
        if not df.empty:
            all_dataframes.append(df)

    # --- 3. Load ---
    if all_dataframes:
        full_df = pd.concat(all_dataframes, ignore_index=True)
        load_data_to_db(full_df, engine)
    else:
        logger.warning("No data transformed successfully.")
        print("No data transformed successfully.")


if __name__ == "__main__":
    main()