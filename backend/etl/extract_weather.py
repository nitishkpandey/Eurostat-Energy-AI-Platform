"""
Open-Meteo Historical Weather Extractor
Pulls historical heating/cooling degree days and average temperatures for major EU capitals
to correlate with energy consumption.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import requests
import pandas as pd

logger = logging.getLogger(__name__)

# Major European Capitals coordinates (Lat, Lon)
EU_CAPITALS = {
    "FR": {"country_name": "France", "lat": 48.8566, "lon": 2.3522},
    "DE": {"country_name": "Germany", "lat": 52.5200, "lon": 13.4050},
    "IT": {"country_name": "Italy", "lat": 41.9028, "lon": 12.4964},
    "ES": {"country_name": "Spain", "lat": 40.4168, "lon": -3.7038},
    "PL": {"country_name": "Poland", "lat": 52.2297, "lon": 21.0122},
    "NL": {"country_name": "Netherlands", "lat": 52.3676, "lon": 4.9041},
}

def fetch_historical_weather(start_date: str = "2020-01-01", end_date: str | None = None) -> pd.DataFrame:
    """
    Fetches historical daily mean temperatures for EU capitals.
    """
    if not end_date:
        end_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    logger.info(f"Fetching historical weather data from {start_date} to {end_date}...")
    
    all_weather_data = []

    for country_code, capital in EU_CAPITALS.items():
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": capital["lat"],
            "longitude": capital["lon"],
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_mean",
            "timezone": "Europe/Berlin"
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "daily" in data:
                df = pd.DataFrame(data["daily"])
                df["country_code"] = country_code
                df["country_name"] = capital["country_name"]
                all_weather_data.append(df)
                logger.info(f"Successfully fetched weather for {country_code}")

        except Exception as e:
            logger.error(f"Failed to fetch weather for {country_code}: {e}")

    if not all_weather_data:
        return pd.DataFrame()

    final_df = pd.concat(all_weather_data, ignore_index=True)
    final_df.rename(columns={"time": "observation_date", "temperature_2m_mean": "mean_temp_celsius"}, inplace=True)
    
    return final_df


def weather_to_observations(weather_df: pd.DataFrame) -> pd.DataFrame:
    """Convert daily weather records into yearly observation rows."""
    if weather_df.empty:
        return pd.DataFrame()

    normalized = weather_df.copy()
    normalized["observation_date"] = pd.to_datetime(normalized["observation_date"], errors="coerce")
    normalized = normalized.dropna(subset=["observation_date", "mean_temp_celsius", "country_code"])

    if normalized.empty:
        return pd.DataFrame()

    yearly = (
        normalized.assign(year=normalized["observation_date"].dt.year)
        .groupby(["country_code", "country_name", "year"], as_index=False)["mean_temp_celsius"]
        .mean()
        .rename(columns={"mean_temp_celsius": "value"})
    )

    yearly["dataset_code"] = "open_meteo_weather"
    yearly["indicator_code"] = "TEMP_MEAN"
    yearly["indicator_label"] = "Mean daily temperature"
    yearly["unit_code"] = "degC"
    yearly["unit_label"] = "Degree Celsius"
    yearly["time"] = pd.to_datetime(yearly["year"].astype(str), format="%Y")
    yearly["load_timestamp"] = datetime.now()

    return yearly[
        [
            "dataset_code",
            "country_code",
            "country_name",
            "indicator_code",
            "indicator_label",
            "unit_code",
            "unit_label",
            "time",
            "value",
            "load_timestamp",
        ]
    ]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = fetch_historical_weather()
    print(df.head())
