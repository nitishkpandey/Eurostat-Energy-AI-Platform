"""ETL transform module.

Converts raw Eurostat JSON-stat responses into clean Pandas DataFrames.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def detect_indicator_dimension(dimensions: Dict[str, Any], indicators: List[str]) -> Optional[str]:
    """Identify which dimension key corresponds to the 'indicator' concept."""
    for dim_name, dim_info in dimensions.items():
        labels = dim_info.get("category", {}).get("label", {})
        if any(ind in labels for ind in indicators):
            return dim_name
    return None


def unravel_index(flat_index: int, sizes: List[int]) -> List[int]:
    """Convert a flat index from Eurostat's JSON format into multi-dimensional coordinates."""
    coords = []
    for size in reversed(sizes):
        coords.append(flat_index % size)
        flat_index //= size
    return list(reversed(coords))


def transform_dataset(dataset_code: str, data: Dict[str, Any], target_indicators: List[str]) -> pd.DataFrame:
    """Transform raw JSON data from Eurostat into a clean DataFrame."""
    dim = data["dimension"]
    dim_ids = data.get("id", list(dim.keys()))
    sizes = data["size"]
    value_data = data["value"]

    labels = {k: dim[k]["category"]["label"] for k in dim if "category" in dim[k]}
    indexes = [dim[d]["category"]["index"] for d in dim_ids]

    indicator_dim = detect_indicator_dimension(dim, target_indicators)
    if not indicator_dim:
        logger.warning("Could not detect indicator dimension in dataset %s", dataset_code)
        return pd.DataFrame()

    result = []

    for flat_index_str, val in value_data.items():
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            continue

        idx = unravel_index(int(flat_index_str), sizes)
        keys = [list(indexes[i].keys())[idx[i]] for i in range(len(idx))]
        dim_map = {dim_ids[i]: keys[i] for i in range(len(dim_ids))}

        indicator = dim_map.get(indicator_dim)
        if indicator not in target_indicators:
            continue

        result.append({
            "dataset_code": dataset_code,
            "country_code": dim_map.get("geo"),
            "country_name": labels.get("geo", {}).get(dim_map.get("geo"), dim_map.get("geo")),
            "indicator_code": indicator,
            "indicator_label": labels.get(indicator_dim, {}).get(indicator),
            "unit_code": dim_map.get("unit"),
            "unit_label": labels.get("unit", {}).get(dim_map.get("unit")),
            "time": dim_map.get("time"),
            "value": val_float,
        })

    logger.info("Transformed %d rows for %s.", len(result), dataset_code)

    if not result:
        return pd.DataFrame()

    df = pd.DataFrame(result)

    # Remove duplicates
    num_duplicates = df.duplicated().sum()
    if num_duplicates > 0:
        logger.info("Removing %d duplicate rows from %s.", num_duplicates, dataset_code)
        df = df.drop_duplicates()

    # Drop rows with missing critical values
    critical_cols = ["country_code", "country_name", "indicator_code", "indicator_label", "time", "value"]
    missing_count = df[critical_cols].isnull().sum().sum()
    if missing_count > 0:
        logger.info("Dropping rows with %d missing critical values in %s.", missing_count, dataset_code)
        df = df.dropna(subset=critical_cols)

    # Parse date and add load timestamp
    df["time"] = pd.to_datetime(df["time"], format="%Y")
    df["load_timestamp"] = datetime.now()

    logger.info("Cleaned data: %d rows remaining for %s.", len(df), dataset_code)
    return df
