"""
Open-Meteo Historical Weather Extractor
Pulls historical heating/cooling degree days and average temperatures for major EU capitals
to correlate with energy consumption.
"""

import logging
import requests
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Major European Capitals coordinates (Lat, Lon)
EU_CAPITALS = {
    "FR": (48.8566, 2.3522),   # Paris
    "DE": (52.5200, 13.4050),  # Berlin
    "IT": (41.9028, 12.4964),  # Rome
    "ES": (40.4168, -3.7038),  # Madrid
    "PL": (52.2297, 21.0122),  # Warsaw
    "NL": (52.3676, 4.9041),   # Amsterdam
}

def fetch_historical_weather(start_date: str = "2020-01-01", end_date: str | None = None) -> pd.DataFrame:
    """
    Fetches historical daily mean temperatures for EU capitals.
    """
    if not end_date:
        end_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    logger.info(f"Fetching historical weather data from {start_date} to {end_date}...")
    
    all_weather_data = []

    for country_code, (lat, lon) in EU_CAPITALS.items():
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
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
                all_weather_data.append(df)
                logger.info(f"Successfully fetched weather for {country_code}")

        except Exception as e:
            logger.error(f"Failed to fetch weather for {country_code}: {e}")

    if not all_weather_data:
        return pd.DataFrame()

    final_df = pd.concat(all_weather_data, ignore_index=True)
    final_df.rename(columns={"time": "observation_date", "temperature_2m_mean": "mean_temp_celsius"}, inplace=True)
    
    return final_df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = fetch_historical_weather()
    print(df.head())
